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

export default PowerBreakdown
