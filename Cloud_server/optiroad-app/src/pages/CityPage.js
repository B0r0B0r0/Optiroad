"use client"

import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import "../assets/styles/CityPage.css"
import CityMap from "../components/CityMap"
import CameraList from "../components/CameraList"
import { FaArrowLeft, FaChartLine, FaTimes } from "react-icons/fa"
import Sidebar from "../components/Sidebar"
import { getCityDevices } from "../services/cityService"


const getVideoId = (url) => {
  const matchEmbed = url.match(/\/embed\/([^?]+)/)
  if (matchEmbed) return matchEmbed[1]
  const matchWatch = url.match(/v=([^&]+)/)
  if (matchWatch) return matchWatch[1]
  return ""
}


const CityPage = () => {
  const { cityName } = useParams()
  const navigate = useNavigate()
  const normalizedCityName = cityName ? cityName.toLowerCase() : "none"

  const [activeCamera, setActiveCamera] = useState(null)
  const [loading, setLoading] = useState(true)
  const [cityData, setCityData] = useState(null)

useEffect(() => {
  const stored = localStorage.getItem(`city:${normalizedCityName}`)
  const coordsRaw = localStorage.getItem(`city:coords:${normalizedCityName}`)

  if (!stored || !coordsRaw) {
    setLoading(false)
    return
  }

  const cityMeta = JSON.parse(stored)
  const { lat, lon } = JSON.parse(coordsRaw)

  if (!lat || !lon || isNaN(lat) || isNaN(lon)) {
    console.warn("Coordonate invalide:", lat, lon)
    setLoading(false)
    return
  }

  // Initialize city data immediately without cameras
  const nextData = {
    name: cityMeta.name,
    county: cityMeta.county,
    country: cityMeta.country,
    center: [Number(lat), Number(lon)],
    cameras: [],
    total: 0,
    online: 0,
    offline: 0,
  }

  setCityData(nextData)
  setLoading(false)

  // Now fetch devices separately (without blocking the first render)
  setCamerasLoading(true)
  getCityDevices({
    country: cityMeta.country,
    county: cityMeta.county,
    city: cityMeta.name
  })
    .then((devices) => {
      const onlineCount = devices.filter((d) => d.status === "online").length
      const offlineCount = devices.length - onlineCount

      setCityData((prev) => ({
        ...prev,
        cameras: devices,
        total: devices.length,
        online: onlineCount,
        offline: offlineCount,
      }))
    })
    .catch((err) => {
      console.error("Eroare la încărcarea camerelor:", err)
      // Optionally show error somewhere
    })
    .finally(() => {
      setCamerasLoading(false)
    })

}, [normalizedCityName])
  const [camerasLoading, setCamerasLoading] = useState(true)
  const handleMarkerClick = (camera) => {
    setActiveCamera(camera)
  }

  const handleCameraClick = (camera) => {
    setActiveCamera(camera)
  }

  const closeVideo = () => {
    setActiveCamera(null)
  }

  const goBack = () => {
    localStorage.removeItem(`city:${normalizedCityName}`);
    localStorage.removeItem(`city:coords:${normalizedCityName}`);
    navigate("/");
  }


  const goToAnalytics = () => {
    navigate(`/city/${normalizedCityName}/analytics`);
  }

  if (loading || !cityData) {
    return <div className="loading-screen">Loading city data...</div>
  }

  return (
    <>
      <Sidebar />
      <div className="city-page">
        <h1 className="city-title">{cityData.name}</h1>

        <div className="city-stats">
          <div className="camera-stat">
            <span className="camera-icon">📹</span> Cameras: {cityData.total}
          </div>
          <div className="camera-stat online">
            <span className="status-dot online"></span> Online: {cityData.online}
          </div>
          <div className="camera-stat offline">
            <span className="status-dot offline"></span> Offline: {cityData.offline}
          </div>
        </div>

        <div className="city-content">
          <div className="map-container">
            <CityMap
              cityName={cityData.name}
              center={cityData.center}
              cameras={cityData.cameras}
              onMarkerClick={handleMarkerClick}
            />
          </div>

          <div className="camera-container">
            <h2>Cameras</h2>
            {camerasLoading ? (
              <div className="cameras-loading">Loading cameras...</div>
            ) : (
              <CameraList
                cameras={cityData.cameras}
                onCameraClick={handleCameraClick}
              />
            )}
          </div>

        </div>

        <div className="action-buttons">
          <button className="action-btn back-btn" onClick={goBack}>
            <FaArrowLeft className="btn-icon" />
            <span className="btn-text">Back</span>
          </button>
          <button className="action-btn analytics-btn" onClick={goToAnalytics}>
            <FaChartLine className="btn-icon" />
            <span className="btn-text">Analytics</span>
          </button>
        </div>

        {activeCamera && (
          <div className="camera-popup-overlay" onClick={closeVideo}>
            <div className="camera-popup-content" onClick={(e) => e.stopPropagation()}>
              <div className="camera-popup-header">
                <h3>Camera {activeCamera.id}</h3>
                <button className="camera-popup-close" onClick={closeVideo}>
                  <FaTimes />
                </button>
              </div>
              <div className="camera-popup-info">
                <p><strong>Location:</strong> {activeCamera.location}</p>
                <p><strong>Status:</strong> <span className={activeCamera.status}>{activeCamera.status}</span></p>
              </div>
              <div className="camera-popup-video">
                <img
                  src={activeCamera.videoUrl}
                  alt={`Camera ${activeCamera.id}`}
                  style={{ width: "100%", height: "400px", borderRadius: "8px", objectFit: "cover" }}
                />


                <div className="video-overlay-blocker"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default CityPage
