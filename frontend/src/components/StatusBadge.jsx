export function DeviceIcon({ type, isOn }) {
  if (type === 'fan') {
    return (
      <span className={`device-icon fan-icon ${isOn ? 'active' : ''}`}>
        <span />
      </span>
    )
  }

  return <span className={`device-icon light-icon ${isOn ? 'active' : ''}`} />
}

function StatusBadge({ status }) {
  const isOn = status === 'ON'

  return (
    <span className={`status-pill ${isOn ? 'on' : 'off'}`}>
      {status}
    </span>
  )
}

export default StatusBadge
