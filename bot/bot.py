import asyncio
import os
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name('.env'))

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', '').rstrip('/')
ALERT_CHANNEL_ID = os.getenv('ALERT_CHANNEL_ID')
VALID_ROOMS = {'drawing', 'work1', 'work2'}
ASSUMED_RATE_BDT_PER_KWH = 10

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
seen_alerts = set()


class BackendUnavailable(Exception):
    pass


async def fetch_json(path):
    if not API_BASE_URL:
        raise BackendUnavailable

    url = f'{API_BASE_URL}{path}'
    timeout = aiohttp.ClientTimeout(total=8)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise BackendUnavailable
                return await response.json()
    except (aiohttp.ClientError, asyncio.TimeoutError):
        raise BackendUnavailable


async def fetch_snapshot():
    return await fetch_json('/snapshot/')


def get_rooms(snapshot):
    rooms = snapshot.get('rooms', [])
    return rooms if isinstance(rooms, list) else []


def get_devices(room):
    devices = room.get('devices', [])
    return devices if isinstance(devices, list) else []


def count_on_devices(room, device_type):
    return sum(
        1
        for device in get_devices(room)
        if device.get('device_type') == device_type and device.get('status') == 'ON'
    )


def room_power(room):
    return sum(device.get('current_power', 0) or 0 for device in get_devices(room))


def total_devices(snapshot):
    summary = snapshot.get('summary', {})
    return summary.get('total_devices') or sum(
        len(get_devices(room)) for room in get_rooms(snapshot)
    )


def format_room_summary(room):
    fans_on = count_on_devices(room, 'fan')
    lights_on = count_on_devices(room, 'light')
    power = room_power(room)

    if fans_on == 0 and lights_on == 0:
        state = 'all devices OFF'
    else:
        fan_text = f'{fans_on} fan{"s" if fans_on != 1 else ""} ON'
        light_text = f'{lights_on} light{"s" if lights_on != 1 else ""} ON'
        state = f'{fan_text}, {light_text}'

    return f'{room.get("name", "Unknown Room")}: {state} | {power}W'


def format_alert(alert):
    severity = str(alert.get('severity', 'info')).upper()
    message = alert.get('message', 'Alert details unavailable.')
    return f'[{severity}] {message}'


def room_name_by_slug(snapshot):
    return {
        room.get('slug'): room.get('name')
        for room in get_rooms(snapshot)
        if room.get('slug') and room.get('name')
    }


def get_alert_room_name(alert, rooms_by_slug):
    room_slug = alert.get('room')
    return rooms_by_slug.get(room_slug) or 'Office'


def stable_alert_key(alert, room_name):
    severity = alert.get('severity', 'info')
    message = alert.get('message', '')
    return f'{severity}|{room_name}|{message}'


def format_proactive_alert(alert, room_name):
    message = alert.get('message', 'Alert details unavailable.')

    if room_name != 'Office':
        message = message.replace(f' in {room_name}', '')

    return (
        '⚠️ Office Alert\n'
        f'Room: {room_name}\n'
        f'Issue: {message}'
    )


def get_alert_channel_id():
    if not ALERT_CHANNEL_ID:
        return None

    try:
        return int(ALERT_CHANNEL_ID)
    except ValueError:
        return None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    if ALERT_CHANNEL_ID and not proactive_alerts.is_running():
        proactive_alerts.start()


@bot.command(name='help')
async def help_command(ctx):
    message = (
        '**Office Energy Monitor Commands**\n'
        '`!status` - Show current office status by room\n'
        '`!room drawing` - Show device details for Drawing Room\n'
        '`!room work1` - Show device details for Work Room 1\n'
        '`!room work2` - Show device details for Work Room 2\n'
        '`!usage` - Show current power and demo cost estimate\n'
        '`!alerts` - Show active backend alerts'
    )
    await ctx.reply(message)


@bot.command(name='status')
async def status_command(ctx):
    try:
        snapshot = await fetch_snapshot()
    except BackendUnavailable:
        await ctx.reply('Backend is not reachable right now.')
        return

    summary = snapshot.get('summary', {})
    rooms = get_rooms(snapshot)

    lines = ['**Office Status**', '']
    lines.extend(format_room_summary(room) for room in rooms)
    lines.extend([
        '',
        f'Total Power: {summary.get("total_power", 0)}W',
        f'Devices ON: {summary.get("devices_on", 0)}/{total_devices(snapshot)}',
        f'Active Alerts: {summary.get("active_alerts", 0)}',
    ])

    await ctx.reply('\n'.join(lines))


@bot.command(name='room')
async def room_command(ctx, room_name=None):
    if not room_name or room_name.lower() not in VALID_ROOMS:
        await ctx.reply('Room not found. Try drawing, work1, or work2.')
        return

    try:
        snapshot = await fetch_snapshot()
    except BackendUnavailable:
        await ctx.reply('Backend is not reachable right now.')
        return

    room = next(
        (item for item in get_rooms(snapshot) if item.get('slug') == room_name.lower()),
        None,
    )

    if not room:
        await ctx.reply('Room not found. Try drawing, work1, or work2.')
        return

    devices = sorted(
        get_devices(room),
        key=lambda item: (item.get('device_type') != 'light', item.get('name', '')),
    )
    lines = [f'**{room.get("name", room_name)} Details**', '']

    for device in devices:
        lines.append(
            f'{device.get("name", "Device")}: '
            f'{device.get("status", "UNKNOWN")} | '
            f'{device.get("current_power", 0)}W'
        )

    lines.extend(['', f'Total Room Power: {room_power(room)}W'])
    await ctx.reply('\n'.join(lines))


@bot.command(name='usage')
async def usage_command(ctx):
    try:
        snapshot = await fetch_snapshot()
    except BackendUnavailable:
        await ctx.reply('Backend is not reachable right now.')
        return

    usage = snapshot.get('usage', {})
    total_power = usage.get('total_power', snapshot.get('summary', {}).get('total_power', 0))
    hourly_kwh = total_power / 1000
    office_day_kwh = hourly_kwh * 8
    estimated_cost = office_day_kwh * ASSUMED_RATE_BDT_PER_KWH
    room_usage = usage.get('room_usage', [])

    lines = [
        '**Power Usage**',
        '',
        f'Total Power Now: {total_power}W',
        '',
        'Room Breakdown:',
    ]

    for room in room_usage if isinstance(room_usage, list) else []:
        lines.append(f'- {room.get("room", "Unknown Room")}: {room.get("power", 0)}W')

    lines.extend([
        '',
        f'Estimated Hourly Usage: {hourly_kwh:.3f} kWh',
        f'Estimated 8-hour Office-Day Usage: {office_day_kwh:.3f} kWh',
        f'Estimated Daily Cost: {estimated_cost:.2f} BDT',
        'Cost uses an assumed demo rate of 10 BDT/kWh.',
    ])

    await ctx.reply('\n'.join(lines))


@bot.command(name='alerts')
async def alerts_command(ctx):
    try:
        snapshot = await fetch_snapshot()
    except BackendUnavailable:
        await ctx.reply('Backend is not reachable right now.')
        return

    alerts = snapshot.get('alerts', [])

    if not isinstance(alerts, list) or not alerts:
        await ctx.reply('No active alerts right now. Everything looks normal.')
        return

    lines = ['**Active Alerts**', '']
    lines.extend(format_alert(alert) for alert in alerts)
    await ctx.reply('\n'.join(lines))


@tasks.loop(seconds=30)
async def proactive_alerts():
    try:
        snapshot = await fetch_snapshot()
    except BackendUnavailable:
        return

    alert_channel_id = get_alert_channel_id()
    channel = bot.get_channel(alert_channel_id) if alert_channel_id else None

    if not channel:
        return

    alerts = snapshot.get('alerts', [])

    if not isinstance(alerts, list):
        return

    rooms_by_slug = room_name_by_slug(snapshot)

    for alert in alerts:
        room_name = get_alert_room_name(alert, rooms_by_slug)
        alert_key = stable_alert_key(alert, room_name)

        if alert_key in seen_alerts:
            continue

        seen_alerts.add(alert_key)
        await channel.send(format_proactive_alert(alert, room_name))


if not DISCORD_TOKEN:
    raise RuntimeError('DISCORD_TOKEN is not set. Create bot/.env first.')

bot.run(DISCORD_TOKEN)
