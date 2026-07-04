import { useEffect, useMemo, useState } from 'react'
import { getSnapshot, toggleDevice } from './api'
import AlertsPanel from './components/AlertsPanel'
import Header from './components/Header'
import OfficeLayout from './components/OfficeLayout'
import PowerBreakdown from './components/PowerBreakdown'
import RoomCard from './components/RoomCard'
import SummaryCards from './components/SummaryCards'
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

  async function handleToggleDevice(deviceId) {
    try {
      await toggleDevice(deviceId)
      const data = await getSnapshot()
      setSnapshot(data)
      setError('')
    } catch {
      setError('Could not toggle device. Is Django running on port 8000?')
    } finally {
      setLoading(false)
    }
  }

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
      <Header updatedAt={updated_at} />

      {error && <p className="error-banner">{error}</p>}

      <SummaryCards summary={summary} usage={usage} />

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
              onToggleDevice={handleToggleDevice}
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
