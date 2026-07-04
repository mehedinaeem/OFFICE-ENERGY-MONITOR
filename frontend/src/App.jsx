import { useEffect, useState } from 'react'
import { getSnapshot } from './api'
import './App.css'

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

  if (loading) {
    return (
      <main className="page">
        <h1>Office Energy Monitor</h1>
        <p className="status">Loading backend snapshot...</p>
      </main>
    )
  }

  if (error && !snapshot) {
    return (
      <main className="page">
        <h1>Office Energy Monitor</h1>
        <p className="error">{error}</p>
      </main>
    )
  }

  const { summary, usage, rooms, alerts, updated_at } = snapshot

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>Office Energy Monitor</h1>
          <p>Live backend snapshot, polling every 2 seconds.</p>
        </div>
        <div className="timestamp">
          Updated: {new Date(updated_at).toLocaleString()}
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="summary-grid" aria-label="Energy summary">
        <div className="summary-card">
          <span>Total Rooms</span>
          <strong>{summary.total_rooms}</strong>
        </div>
        <div className="summary-card">
          <span>Total Devices</span>
          <strong>{summary.total_devices}</strong>
        </div>
        <div className="summary-card">
          <span>Devices ON</span>
          <strong>{summary.devices_on}</strong>
        </div>
        <div className="summary-card">
          <span>Total Power</span>
          <strong>{summary.total_power}W</strong>
        </div>
        <div className="summary-card">
          <span>Active Alerts</span>
          <strong>{summary.active_alerts}</strong>
        </div>
      </section>

      <section className="section">
        <h2>Room Usage</h2>
        <div className="room-usage">
          {usage.room_usage.map((room) => (
            <div className="usage-row" key={room.slug}>
              <span>{room.room}</span>
              <span>
                {room.devices_on}/{room.total_devices} on
              </span>
              <strong>{room.power}W</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>Rooms And Devices</h2>
        <div className="rooms">
          {rooms.map((room) => (
            <article className="room" key={room.slug}>
              <h3>{room.name}</h3>
              <ul>
                {room.devices.map((device) => (
                  <li key={device.id}>
                    <span>
                      {device.name} ({device.device_type})
                    </span>
                    <span className={device.status === 'ON' ? 'on' : 'off'}>
                      {device.status} - {device.current_power}W
                    </span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>Alerts</h2>
        {alerts.length === 0 ? (
          <p>No active alerts.</p>
        ) : (
          <ul className="alerts">
            {alerts.map((alert) => (
              <li key={alert.id}>
                <strong>{alert.severity}</strong>: {alert.message}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}

export default App
