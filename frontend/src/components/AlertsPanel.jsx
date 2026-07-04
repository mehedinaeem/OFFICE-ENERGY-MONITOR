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

export default AlertsPanel
