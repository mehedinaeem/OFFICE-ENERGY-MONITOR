import { DeviceIcon } from './StatusBadge'

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
              {room.devices.map((device) => (
                <DeviceIcon
                  key={device.id}
                  type={device.device_type}
                  isOn={device.status === 'ON'}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default OfficeLayout
