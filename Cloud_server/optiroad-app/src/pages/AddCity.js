"use client"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import "../assets/styles/AddCity.css"
import { FaArrowLeft } from "react-icons/fa"
import Sidebar from "../components/Sidebar"
import { addCity } from "../services/cityService"





const AddCity = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    country: "",
    county: "",
    city: ""
  })
  
  const goBack = () => {
    navigate("/")
  }
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    addCity(formData)
    .then((response) => {
      if (response.error) {
        alert(`Error: ${response.error}`)
      } else {
        alert("City added successfully!")
        navigate("/")
      }
    })
  }

  return (
    <>
    <Sidebar />
    <div className="add-city-container">
      <h1 className="add-city-title">Configured Cities</h1>

      <form className="add-city-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="country">Country</label>
          <input
            type="text"
            id="country"
            name="country"
            placeholder="Enter country"
            value={formData.country}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="county">County</label>
          <input
            type="text"
            id="county"
            name="county"
            placeholder="Enter county"
            value={formData.county}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="city">City</label>
          <input
            type="text"
            id="city"
            name="city"
            placeholder="Enter city"
            value={formData.city}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="register-btn">
          Register
        </button>
        <button className="action-btn back-btn" style={{ marginTop: "20px" }} onClick={goBack}>
          <FaArrowLeft className="btn-icon" />
          <span className="btn-text">Back</span>
        </button>
      </form>
    </div>
    </>
  )
}

export default AddCity
