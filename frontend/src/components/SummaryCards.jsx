function MetricCard({ label, value, detail, tone = 'default' }) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </article>
  )
}

function formatKwh(value) {
  return `${Number(value).toFixed(2)} kWh`
}

function formatBdt(value) {
  return `${Number(value).toFixed(2)} BDT`
}

function SummaryCards({ summary, usage }) {
  return (
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
      <MetricCard
        label="Estimated Hourly Usage"
        value={formatKwh(usage.estimated_hourly_kwh)}
        detail="Based on current power"
      />
      <MetricCard
        label="Estimated Office-Day Usage"
        value={formatKwh(usage.estimated_daily_kwh)}
        detail="Based on 8 hours"
      />
      <MetricCard
        label="Estimated Daily Cost"
        value={formatBdt(usage.estimated_daily_cost)}
        detail={usage.assumption_label}
      />
    </section>
  )
}

export default SummaryCards
