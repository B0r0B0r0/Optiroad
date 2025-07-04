import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { sendContactEmail } from "../services/emailService"; 
import { FaHeadset } from "react-icons/fa";
import "../assets/styles/Contact.css";

const Contact = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const [successMsg, setSuccessMsg] = useState("");
  const [errMsg, setErrMsg] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) {
      setErrMsg("Please fill in all fields.");
      return;
    }

    try {
      await sendContactEmail(formData); 
      setSuccessMsg("Message sent successfully!");
      setFormData({ name: "", email: "", message: "" });
    } catch (error) {
      setErrMsg("Failed to send message. Try again later.");
    }
  };

  return (
    <div className="contact-content">
      <div className="top-section">
        <FaHeadset className="contact-icon"/>
        <h1>Contact Us</h1>
      </div>
      {successMsg && <p className="success-msg">{successMsg}</p>}
      {errMsg && <p className="errmsg">{errMsg}</p>}

      <form onSubmit={handleSubmit}>
        <label>Name:</label>
        <input className= "input-field" type="text" name="name" value={formData.name} onChange={handleChange} required />

        <label>Email:</label>
        <input className= "input-field" type="email" name="email" value={formData.email} onChange={handleChange} required />

        <label>Message:</label>
        <textarea className= "input-field" name="message" value={formData.message} onChange={handleChange} required></textarea>

        <button type="submit" className="contact-button">Send Message</button>
      </form>

      <p>Need a registration key? <span className="link" onClick={() => navigate("/request-key")}>Click here</span></p>
    </div>
  );
};

export default Contact;
