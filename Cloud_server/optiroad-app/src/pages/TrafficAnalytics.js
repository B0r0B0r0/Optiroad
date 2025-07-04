"use client"

import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
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
} from "chart.js"
import { FaFileExport, FaFilePdf, FaSpinner, FaArrowLeft } from "react-icons/fa"
import "../assets/styles/TrafficAnalytics.css"
import Sidebar from "../components/Sidebar"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const TrafficAnalytics = () => {
  const { cityName } = useParams()
  const navigate = useNavigate()

  const normalizedCity = cityName?.toLowerCase()
  const [exportingCSV, setExportingCSV] = useState(false)
  const [exportingPDF, setExportingPDF] = useState(false)

  const meta = localStorage.getItem(`city:${normalizedCity}`)

  if (!meta || !normalizedCity) {
    return <div style={{ padding: "2rem" }}>No valid city selected. Return to homepage.</div>
  }

  const cityLabel = normalizedCity.charAt(0).toUpperCase() + normalizedCity.slice(1)

  const goBack = () => {
    navigate(`/city/${normalizedCity}`)
  }

  const trafficData = {
    tecuci: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      datasets: [
        {
          label: "Before Optimization",
          data: [120, 115, 125, 130, 128, 135, 140, 138, 142, 130, 125, 120],
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.2)",
        },
        {
          label: "After Optimization",
          data: [120, 110, 105, 95, 85, 80, 75, 70, 65, 60, 55, 50],
          borderColor: "rgba(54, 162, 235, 1)",
          backgroundColor: "rgba(54, 162, 235, 0.2)",
        },
      ],
    },
    "cluj-napoca": { /* similar */ },
    timisoara: { /* similar */ },
  }

  const currentData = trafficData[normalizedCity]

  if (!currentData) {
    return <div style={{ padding: "2rem" }}>No analytics available for {cityLabel}.</div>
  }

  const handleExportCSV = () => {
    if (exportingCSV) return
    setExportingCSV(true)

    setTimeout(() => {
      const data = currentData
      let csvContent = "Month,Before Optimization,After Optimization\n"

      data.labels.forEach((month, index) => {
        csvContent += `${month},${data.datasets[0].data[index]},${data.datasets[1].data[index]}\n`
      })

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.setAttribute("href", url)
      link.setAttribute("download", `${normalizedCity}_traffic_data.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      setExportingCSV(false)
    }, 2000)
  }

  const handleExportPDF = async () => {
    if (exportingPDF) return
    setExportingPDF(true)

    try {
      const chartContainer = document.querySelector(".chart-container")
      const canvas = await html2canvas(chartContainer, { scale: 2 })
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

      pdf.addImage(imgData, "PNG", (pageWidth - imgWidth) / 2, 40, imgWidth, imgHeight)

      pdf.setFontSize(18)
      pdf.text(
        `Traffic Light Optimization – ${cityLabel}`,
        pageWidth / 2,
        30,
        { align: "center" }
      )

      pdf.setFontSize(10)
      pdf.text(
        `Generated on ${new Date().toLocaleDateString()}`,
        pageWidth - 40,
        pageHeight - 20,
        { align: "right" }
      )

      pdf.save(`${normalizedCity}_traffic_data.pdf`)
    } catch (err) {
      console.error("PDF export failed:", err)
    }

    setExportingPDF(false)
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: {
        display: true,
        text: "Traffic Light Waiting Time Evolution (seconds)",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Average Waiting Time (seconds)",
        },
      },
      x: {
        title: {
          display: true,
          text: "Month",
        },
      },
    },
  }

  return (
    <>
      <Sidebar />
      <div className="traffic-analytics-container">
        <h1 className="analytics-title">
          Traffic Analytics – {cityLabel}
        </h1>

        <div className="chart-container">
          <Line options={options} data={currentData} />
        </div>

        <div className="analytics-summary">
          <h2>Optimization Summary</h2>
          <p>
            The traffic light optimization system has reduced average waiting times by
            <span className="highlight">
              {" "}
              {Math.round(
                ((currentData.datasets[0].data[0] - currentData.datasets[1].data[11]) /
                  currentData.datasets[0].data[0]) *
                  100
              )}
              %
            </span>{" "}
            over the past year.
          </p>
          <p>This has resulted in reduced congestion, lower emissions, and improved traffic flow throughout the city.</p>
        </div>

        <div className="export-buttons">
          <button className="action-btn back-btn" onClick={goBack}>
            <FaArrowLeft className="btn-icon" />
            <span className="btn-text">Back</span>
          </button>

          <button
            className={`export-btn export-csv ${exportingCSV ? "loading" : ""}`}
            onClick={handleExportCSV}
            disabled={exportingCSV || exportingPDF}
          >
            {exportingCSV ? (
              <>
                <FaSpinner className="spinner" />
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <FaFileExport />
                <span>Export to CSV</span>
              </>
            )}
          </button>

          <button
            className={`export-btn export-pdf ${exportingPDF ? "loading" : ""}`}
            onClick={handleExportPDF}
            disabled={exportingCSV || exportingPDF}
          >
            {exportingPDF ? (
              <>
                <FaSpinner className="spinner" />
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <FaFilePdf />
                <span>Export to PDF</span>
              </>
            )}
          </button>
        </div>
      </div>
    </>
  )
}

export default TrafficAnalytics
