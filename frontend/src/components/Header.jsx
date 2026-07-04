function Header({ updatedAt }) {
  const updatedDate = new Date(updatedAt)

  return (
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
        <strong>{updatedDate.toLocaleTimeString()}</strong>
        <small>{updatedDate.toLocaleDateString()}</small>
      </div>
    </header>
  )
}

export default Header
