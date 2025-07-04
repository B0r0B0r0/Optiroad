import React, { useState } from "react";
import { sendRequestKey } from "../services/authService";
import "../assets/styles/RequestKey.css";

const RequestKey = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    birthDate: "",
    address: "",
    profession: "",
    workplace: "",
    email: "",
    phoneNumber: "",
    idFront: null,
    idBack: null
  });

  const [errMsg, setErrMsg] = useState("");
  const [errFileMsg, setFileErrMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validateFileType = (file) => {
    if (!file) return false;
    const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
    return allowedTypes.includes(file.type);
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files.length > 0 && !validateFileType(files[0])) {
      setFileErrMsg("Invalid file type! Please upload a JPG or PNG image.");
      return;
    }
    setFileErrMsg("");
    setFormData((prev) => ({ ...prev, [name]: files[0] }));
  };

  const validateAge = (birthDate) => {
    const birth = new Date(birthDate);
    const today = new Date();
    const age = today.getFullYear() - birth.getFullYear();
    return age >= 18;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateAge(formData.birthDate)) {
      setErrMsg("You must be at least 18 years old.");
      return;
    }

    if (!formData.idFront || !formData.idBack) {
      setErrMsg("Please upload both front and back images of your ID.");
      return;
    }

    try {
      await sendRequestKey(formData);
      setSuccessMsg("Request submitted successfully!");
      setFormData({
        firstName: "",
        lastName: "",
        birthDate: "",
        address: "",
        profession: "",
        workplace: "",
        email: "",
        phoneNumber: "",
        idFront: null,
        idBack: null
      });
    } catch (error) {
      setErrMsg("Failed to submit request. Please try again.");
    }
  };

  return (
    <div className="request-key-content">
      <h1>Request Registration Key</h1>
      {successMsg && <p className="success-msg">{successMsg}</p>}
      {errMsg && <p className="errmsg">{errMsg}</p>}

      <form onSubmit={handleSubmit}>
        <label>First Name:</label>
        <input className= "input-field" type="text" name="firstName" value={formData.firstName} onChange={handleChange} required />

        <label>Last Name:</label>
        <input className= "input-field" type="text" name="lastName" value={formData.lastName} onChange={handleChange} required />

        <label>Date of Birth:</label>
        <input className= "input-field" type="date" name="birthDate" value={formData.birthDate} onChange={handleChange} required />

        <label>Address:</label>
        <input className= "input-field" type="text" name="address" value={formData.address} onChange={handleChange} required />

        <label>Profession:</label>
        <input className= "input-field" type="text" name="profession" value={formData.profession} onChange={handleChange} required />

        <label>Workplace:</label>
        <input className= "input-field" type="text" name="workplace" value={formData.workplace} onChange={handleChange} required />

        <label>Email:</label>
        <input className= "input-field" type="email" name="email" value={formData.email} onChange={handleChange} required />
        
        <label>Phone Number:</label>
        <input className="input-field" type="tel" name="phoneNumber" value={formData.phoneNumber || ""} onChange={handleChange} required />
        
        <label>Upload ID Front:</label>
        <input className= "input-field" type="file" name="idFront" accept="image/*" onChange={handleFileChange} required />

        <label>Upload ID Back:</label>
        <input className= "input-field" type="file" name="idBack" accept="image/*" onChange={handleFileChange} required />

        {errFileMsg && <p className="errmsg">{errFileMsg}</p>}
        <p className="file-note">Please upload a JPG or PNG image.</p>

        <button type="submit" className="request-key-button">Submit Request</button>
      </form>
    </div>
  );
};

export default RequestKey;
