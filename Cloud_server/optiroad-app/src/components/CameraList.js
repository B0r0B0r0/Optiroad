"use client"

import "../assets/styles/CameraList.css"

const CameraList = ({ cameras, onCameraClick }) => {
  return (
    <div className="camera-list">
      {cameras.map((camera) => (
        <div key={camera.id} className="camera-item" onClick={() => onCameraClick(camera)}>
          <div className={`status-indicator ${camera.status}`}>{camera.status === "online" ? "Online" : "Offline"}</div>
          <div className="camera-location">{camera.location}</div>
        </div>
      ))}
    </div>
  )
}

export default CameraList
