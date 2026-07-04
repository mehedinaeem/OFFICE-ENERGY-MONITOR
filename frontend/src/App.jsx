import { useEffect, useMemo, useState } from 'react'
import { getSnapshot } from './api'
import './App.css'

const roomDescriptions = {
  drawing: 'Client lounge and shared meeting area',
  work1: 'Primary workstation area',
  work2: 'Secondary workstation area',
}

function DeviceIcon({ type, isOn }) {
  if (type === 'fan') {
    return (
      <span className={`device-icon fan-icon ${isOn ? 'active' : ''}`}>
        <span />
      </span>
    )
  }

  return <span className={`device-icon light-icon ${isOn ? 'active' : ''}`} />
}

function MetricCard({ label, value, detail, tone = 'default' }) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </article>
  )
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
                <span className={`status-pill ${isOn ? 'on' : 'off'}`}>
                  {device.status}
                </span>
                <strong>{device.current_power}W</strong>
              </div>
            </li>
          )
        })}
      </ul>
    </article>
  )
}

function PowerBreakdown({ roomUsage }) {
  const maxPower = Math.max(...roomUsage.map((room) => room.power), 1)

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Power Breakdown</h2>
        <p>Room-wise current draw from active devices.</p>
      </div>

      <div className="power-bars">
        {roomUsage.map((room) => {
          const width = `${Math.max((room.power / maxPower) * 100, 2)}%`

          return (
            <div className="power-row" key={room.slug}>
              <div className="power-label">
                <span>{room.room}</span>
                <strong>{room.power}W</strong>
              </div>
              <div className="bar-track" aria-hidden="true">
                <div className="bar-fill" style={{ width }} />
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

function AlertsPanel({ alerts }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Active Alerts</h2>
        <p>Facilities exceptions generated from the live backend snapshot.</p>
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state">
          <strong>No active alerts</strong>
          <span>All monitored rooms are currently within expected limits.</span>
        </div>
      ) : (
        <ul className="alert-list">
          {alerts.map((alert) => (
            <li className={`alert-card ${alert.severity}`} key={alert.id}>
              <strong>{alert.severity}</strong>
              <p>{alert.message}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function OfficeLayout({ rooms }) {
  return (
    <section className="panel layout-panel">
      <div className="section-heading">
        <h2>Office Layout</h2>
        <p>Top-view room indicators for lights and fans.</p>
      </div>

      <div className="floor-plan">
        {rooms.map((room) => (
          <div className={`floor-room ${room.slug}`} key={room.slug}>
            <div className="floor-room-title">{room.name}</div>
            <div className="floor-devices">
              {room.devices.map((device) => {
                const isOn = device.status === 'ON'

                return (
                  <DeviceIcon
                    key={device.id}
                    type={device.device_type}
                    isOn={isOn}
                  />
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function App() {
  const [snapshot, setSnapshot] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function loadSnapshot() {
      try {
        const data = await getSnapshot()

        if (isMounted) {
          setSnapshot(data)
          setError('')
        }
      } catch {
        if (isMounted) {
          setError('Could not fetch backend data. Is Django running on port 8000?')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadSnapshot()
    const intervalId = setInterval(loadSnapshot, 2000)

    return () => {
      isMounted = false
      clearInterval(intervalId)
    }
  }, [])

  const roomUsageBySlug = useMemo(() => {
    if (!snapshot) {
      return {}
    }

    return Object.fromEntries(
      snapshot.usage.room_usage.map((room) => [room.slug, room])
    )
  }, [snapshot])

  if (loading) {
    return (
      <main className="dashboard-page">
        <section className="loading-panel">
          <h1>Office Energy Monitor</h1>
          <p>Loading live operations snapshot...</p>
        </section>
      </main>
    )
  }

  if (error && !snapshot) {
    return (
      <main className="dashboard-page">
        <section className="loading-panel">
          <h1>Office Energy Monitor</h1>
          <p className="error-banner">{error}</p>
        </section>
      </main>
    )
  }

  const { summary, usage, rooms, alerts, updated_at } = snapshot

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Facilities operations</p>
          <h1>Office Energy Monitor</h1>
          <p className="subtitle">
            Live monitoring for office lights, fans, power usage, and alerts
          </p>
        </div>
        <div className="header-status">
          <span>Last updated</span>
          <strong>{new Date(updated_at).toLocaleTimeString()}</strong>
          <small>{new Date(updated_at).toLocaleDateString()}</small>
        </div>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <section className="metrics-grid" aria-label="Energy summary">
        <MetricCard label="Total Rooms" value={summary.total_rooms} />
        <MetricCard label="Total Devices" value={summary.total_devices} />
        <MetricCard
          label="Devices ON"
          value={summary.devices_on}
          detail={`${summary.total_devices - summary.devices_on} off`}
          tone={summary.devices_on > 0 ? 'success' : 'default'}
        />
        <MetricCard label="Current Power" value={`${summary.total_power}W`} />
        <MetricCard
          label="Active Alerts"
          value={summary.active_alerts}
          tone={summary.active_alerts > 0 ? 'danger' : 'success'}
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Room Status</h2>
          <p>Device state and current load by monitored office room.</p>
        </div>
        <div className="rooms-grid">
          {rooms.map((room) => (
            <RoomCard
              key={room.slug}
              room={room}
              roomUsage={roomUsageBySlug[room.slug]}
            />
          ))}
        </div>
      </section>

      <div className="dashboard-columns">
        <PowerBreakdown roomUsage={usage.room_usage} />
        <AlertsPanel alerts={alerts} />
      </div>

      <OfficeLayout rooms={rooms} />
    </main>
  )
}

export default App
