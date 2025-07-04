"use client"

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import "../assets/styles/CityMap.css"

// Define camera icons
const onlineIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const offlineIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const CityMap = ({ center, cameras, onMarkerClick }) => {
  console.log("CityMap rendered with center:", center, "and cameras:", cameras)
  return (
    <div className="city-map-container">
      <MapContainer center={center} zoom={13} className="city-map">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {cameras.map((camera) => (
          <Marker
            key={camera.id}
            position={[camera.lat, camera.lng]}
            icon={camera.status === "online" ? onlineIcon : offlineIcon}
          >
            <Popup>
              <div className="camera-popup">
                <h3>Camera {camera.id}</h3>
                <p>Location: {camera.location}</p>
                <p>
                  Status: <span className={camera.status}>{camera.status}</span>
                </p>
                <button className="view-live-btn" onClick={() => onMarkerClick(camera)}>
                  View Live
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

export default CityMap
