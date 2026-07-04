import StatusBadge, { DeviceIcon } from './StatusBadge'

const roomDescriptions = {
  drawing: 'Client lounge and shared meeting area',
  work1: 'Primary workstation area',
  work2: 'Secondary workstation area',
}

function RoomCard({ room, roomUsage }) {
  const roomPower = roomUsage?.power ?? 0
  const devicesOn = roomUsage?.devices_on ?? 0
  const totalDevices = roomUsage?.total_devices ?? room.devices.length

  return (
    <article className="room-card">
      <header className="room-card-header">
        <div>
          <h3>{room.name}</h3>
          <p>{room.description || roomDescriptions[room.slug] || 'Office area'}</p>
        </div>
        <div className="room-power">
          <strong>{roomPower}W</strong>
          <span>
            {devicesOn}/{totalDevices} on
          </span>
        </div>
      </header>

      <ul className="device-list">
        {room.devices.map((device) => {
          const isOn = device.status === 'ON'

          return (
            <li key={device.id}>
              <div className="device-name">
                <DeviceIcon type={device.device_type} isOn={isOn} />
                <span>{device.name}</span>
              </div>
              <div className="device-state">
                <StatusBadge status={device.status} />
                <strong>{device.current_power}W</strong>
              </div>
            </li>
          )
        })}
      </ul>
    </article>
  )
}

export default RoomCard
