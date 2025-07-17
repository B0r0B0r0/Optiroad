"use client"

import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { Line } from "react-chartjs-2"
import { jsPDF } from "jspdf"
import html2canvas from "html2canvas"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from "chart.js"
import "chartjs-adapter-date-fns"
import zoomPlugin from "chartjs-plugin-zoom"
import "../assets/styles/TrafficAnalytics.css"
import { getAnalyticsData } from "../services/analyticsService"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale, zoomPlugin)

// Replace with your actual API call


const TrafficAnalytics = () => {
  const [exportingCSV, setExportingCSV] = useState(false)
  const [exportingPDF, setExportingPDF] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [rawData, setRawData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [viewMode, setViewMode] = useState("time")

  const { cityName } = useParams()


  const normalizedCity = cityName?.toLowerCase()


  const meta = localStorage.getItem(`city:${normalizedCity}`)
  const cityLabel = normalizedCity
    ? normalizedCity.charAt(0).toUpperCase() + normalizedCity.slice(1)
    : ""


  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const parsedMeta = JSON.parse(meta)
        const { country, county, name } = parsedMeta

        const result = await getAnalyticsData({ country, county, city: name })


        if (!result || !result.length) {
          setError("No analytics data available.")
          setLoading(false)
          return
        }

        // Filter only records with valid date windows
        const filtered = result.filter((item) => item.window && item.window.start)
        if (!filtered.length) {
          setError("No valid analytics records with dates available.")
          setLoading(false)
          return
        }

        // Sort by start time to ensure chronological order
        filtered.sort((a, b) => new Date(a.window.start).getTime() - new Date(b.window.start).getTime())

        setRawData(filtered)
        setLoading(false)
      } catch (err) {
        console.error("Error fetching analytics:", err)
        setError("Failed to load analytics data. Please try again later.")
        setLoading(false)
      }
    }

    fetchData()
  }, [cityName])

  useEffect(() => {
    if (!rawData.length) return

    let filtered = []

    if (viewMode === "time") {
      filtered = rawData.filter(
        (item) =>
          item.window &&
          item.window.start &&
          typeof item.vehicle_waiting_init === "number" &&
          typeof item.vehicle_waiting_post === "number",
      )
    } else if (viewMode === "mean") {
      filtered = rawData.filter(
        (item) =>
          item.window &&
          item.window.start &&
          Array.isArray(item.init_mean_vector) &&
          item.init_mean_vector.length > 0 &&
          Array.isArray(item.post_mean_vector) &&
          item.post_mean_vector.length > 0,
      )
    }

    if (!filtered.length) {
      setChartData(null)
      return
    }

    filtered.sort((a, b) => new Date(a.window.start).getTime() - new Date(b.window.start).getTime())

    // Create labels based on the time window (each JSON represents one hour)
    const labels = filtered.map((item) => {
      const startTime = new Date(item.window.start)
      const endTime = new Date(item.window.end)
      return {
        start: startTime,
        end: endTime,
        label: `${startTime.toLocaleDateString("ro-RO")} ${startTime.getHours().toString().padStart(2, "0")}:${startTime.getMinutes().toString().padStart(2, "0")}-${endTime.getHours().toString().padStart(2, "0")}:${endTime.getMinutes().toString().padStart(2, "0")}`,
      }
    })

    let beforeData = []
    let afterData = []
    let title = ""
    let yAxisLabel = ""

    if (viewMode === "time") {
      // Use the float values for waiting times
      beforeData = filtered.map((item) => item.vehicle_waiting_init)
      afterData = filtered.map((item) => item.vehicle_waiting_post)
      title = "Vehicle Waiting Times Evolution"
      yAxisLabel = "Waiting Time (seconds)"
    } else if (viewMode === "mean") {
      // Use the mean vectors - calculate average of each vector
      beforeData = filtered.map((item) => {
        const vector = item.init_mean_vector
        return vector.reduce((sum, val) => sum + val, 0) / vector.length
      })
      afterData = filtered.map((item) => {
        const vector = item.post_mean_vector
        return vector.reduce((sum, val) => sum + val, 0) / vector.length
      })
      title = "Mean Vector Values Evolution"
      yAxisLabel = "Mean Vector Value (seconds/vehicles)"
    }

    setChartData({
      labels: labels.map((l) => l.start), // Use start time for chart
      timeLabels: labels, // Keep full time info for tooltips
      datasets: [
        {
          label: "Initial Values",
          data: beforeData,
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.1)",
          borderWidth: 3,
          pointBackgroundColor: "#ef4444",
          pointBorderColor: "#dc2626",
          pointRadius: 6,
          pointHoverRadius: 8,
          tension: 0.4,
        },
        {
          label: "Final Values",
          data: afterData,
          borderColor: "#22c55e",
          backgroundColor: "rgba(34, 197, 94, 0.1)",
          borderWidth: 3,
          pointBackgroundColor: "#22c55e",
          pointBorderColor: "#16a34a",
          pointRadius: 6,
          pointHoverRadius: 8,
          tension: 0.4,
        },
      ],
      title,
      yAxisLabel,
    })
  }, [rawData, viewMode])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      title: {
        display: true,
        text: chartData?.title || "",
        font: {
          size: 18,
          weight: "bold",
        },
        padding: 20,
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "white",
        bodyColor: "white",
        borderColor: "rgba(255, 255, 255, 0.2)",
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          title: (context) => {
            const index = context[0].dataIndex
            if (chartData?.timeLabels && chartData.timeLabels[index]) {
              return chartData.timeLabels[index].label
            }
            return new Date(context[0].parsed.x).toLocaleDateString("ro-RO")
          },
          label: (context) => {
            const value = context.parsed.y.toFixed(2)
            const unit = viewMode === "time" ? " seconds" : ""
            return `${context.dataset.label}: ${value}${unit}`
          },
        },
      },
      zoom: {
        zoom: {
          wheel: {
            enabled: true,
          },
          pinch: {
            enabled: true,
          },
          mode: "xy",
        },
        pan: {
          enabled: true,
          mode: "xy",
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: chartData?.yAxisLabel || "",
          font: {
            size: 14,
            weight: "bold",
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
        ticks: {
          font: {
            size: 12,
          },
        },
      },
      x: {
        type: "time",
        time: {
          displayFormats: {
            hour: "HH:mm",
            day: "MMM dd",
            week: "MMM dd",
            month: "MMM yyyy",
          },
          tooltipFormat: "MMM dd, yyyy HH:mm",
        },
        title: {
          display: true,
          text: "Time Period",
          font: {
            size: 14,
            weight: "bold",
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
          drawOnChartArea: true,
        },
        ticks: {
          font: {
            size: 12,
          },
          maxRotation: 45,
        },
      },
    },
  }

  const calculateAverageSavings = () => {
    if (!chartData || !chartData.datasets[0].data.length) return 0

    const initialData = chartData.datasets[0].data
    const finalData = chartData.datasets[1].data

    let totalSavings = 0
    let validPoints = 0

    for (let i = 0; i < initialData.length; i++) {
      if (initialData[i] > 0 && finalData[i] >= 0) {
        const savings = ((initialData[i] - finalData[i]) / initialData[i]) * 100
        totalSavings += Math.max(0, savings)
        validPoints++
      }
    }

    return validPoints > 0 ? Math.round(totalSavings / validPoints) : 0
  }

  const handleExportCSV = () => {
    if (exportingCSV || !chartData) return
    setExportingCSV(true)

    setTimeout(() => {
      let csvContent = `Time Period,Initial Values,Final Values\n`

      chartData.timeLabels?.forEach((timeInfo, index) => {
        csvContent += `${timeInfo.label},${chartData.datasets[0].data[index]},${chartData.datasets[1].data[index]}\n`
      })

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.setAttribute("href", url)
      link.setAttribute("download", `${cityName}_traffic_${viewMode}_data.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      setExportingCSV(false)
    }, 1500)
  }

  const handleExportPDF = async () => {
    if (exportingPDF) return
    setExportingPDF(true)

    try {
      const chartContainer = document.querySelector(".chart-container")
      if (!chartContainer) return

      const canvas = await html2canvas(chartContainer, {
        scale: 2,
        backgroundColor: "#ffffff",
        useCORS: true,
      })
      const imgData = canvas.toDataURL("image/png")

      const pdf = new jsPDF({
        orientation: "landscape",
        unit: "pt",
        format: "a4",
      })

      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const imgProps = pdf.getImageProperties(imgData)
      const ratio = Math.min(pageWidth / imgProps.width, pageHeight / imgProps.height) * 0.9
      const imgWidth = imgProps.width * ratio
      const imgHeight = imgProps.height * ratio

      pdf.addImage(imgData, "PNG", (pageWidth - imgWidth) / 2, 60, imgWidth, imgHeight)

      pdf.setFontSize(18)
      pdf.text(`Traffic Analytics – ${cityLabel}`, pageWidth / 2, 40, { align: "center" })

      pdf.setFontSize(12)
      pdf.text(`View Mode: ${viewMode === "time" ? "Waiting Times" : "Mean Vector"}`, 40, pageHeight - 40)
      pdf.text(`Average Improvement: ${calculateAverageSavings()}%`, 40, pageHeight - 25)
      pdf.text(`Generated on ${new Date().toLocaleDateString("ro-RO")}`, pageWidth - 40, pageHeight - 25, {
        align: "right",
      })

      pdf.save(`${cityLabel}_traffic_${viewMode}_analytics.pdf`)
    } catch (err) {
      console.error("PDF export failed:", err)
    }

    setExportingPDF(false)
  }

  const resetZoom = () => {
    const chartInstance = ChartJS.getChart("traffic-chart")
    if (chartInstance) {
      chartInstance.resetZoom()
    }
  }

  const goBack = () => {
    window.history.back()
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-card">
          <div className="loading-content">
            <div className="spinner"></div>
            <span className="loading-text">Loading analytics data for {cityName}...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !chartData) {
    return (
      <div className="error-container">
        <div className="error-card">
          <div className="error-header">
            <h2 className="error-title">No Data Available</h2>
            <p className="error-description">{error || `No analytics data available for ${cityName}.`}</p>
          </div>
          <div className="error-content">
            <div className="error-icon">📊</div>
            <p className="error-message">We couldn't find any traffic analytics data for this location.</p>
            <button className="back-button" onClick={goBack}>
              ← Go Back
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="traffic-analytics-container">
      <div className="analytics-wrapper">
        <div className="header-section">
          <button className="back-btn" onClick={goBack}>
            ← Back
          </button>

          <h1 className="analytics-title">Traffic Analytics - {cityLabel}</h1>

          <div className="controls-section">
            <label htmlFor="viewMode" className="control-label">
              Select View:
            </label>
            <select
              id="viewMode"
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="view-selector"
            >
              <option value="time">Waiting Times</option>
              <option value="mean">Mean Vector</option>
            </select>

            <button className="reset-zoom-btn" onClick={resetZoom}>
              Reset Zoom
            </button>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-container" style={{ height: "500px" }}>
            <Line id="traffic-chart" options={chartOptions} data={chartData} />
          </div>
        </div>

        <div className="summary-section">
          <div className="summary-card">
            <div className="summary-header">
              <h3>Optimization Summary</h3>
            </div>
            <div className="summary-content">
              <div className="percentage-display">{calculateAverageSavings()}%</div>
              <p className="percentage-label">
                Average {viewMode === "time" ? "waiting time" : "mean vector"} reduction
              </p>
              <p className="summary-description">
                The traffic light optimization system has improved traffic flow throughout the monitored period,
                resulting in reduced congestion and lower emissions.
              </p>
            </div>
          </div>

          <div className="export-card">
            <div className="export-header">
              <h3>Export Data</h3>
              <p className="export-description">Download your analytics data in different formats</p>
            </div>
            <div className="export-content">
              <button
                onClick={handleExportCSV}
                disabled={exportingCSV || exportingPDF}
                className={`export-btn csv-btn ${exportingCSV ? "loading" : ""}`}
              >
                {exportingCSV ? (
                  <>
                    <div className="spinner-small"></div>
                    Exporting...
                  </>
                ) : (
                  <>📄 Export CSV</>
                )}
              </button>

              <button
                onClick={handleExportPDF}
                disabled={exportingCSV || exportingPDF}
                className={`export-btn pdf-btn ${exportingPDF ? "loading" : ""}`}
              >
                {exportingPDF ? (
                  <>
                    <div className="spinner-small"></div>
                    Exporting...
                  </>
                ) : (
                  <>📊 Export PDF</>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrafficAnalytics
