import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import { FaEye, FaEyeSlash, FaCheck, FaTimes, FaInfoCircle } from "react-icons/fa";
import "../assets/styles/Register.css";

const userRegex = /^[a-zA-Z][a-zA-Z0-9-_]{3,20}$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
const keyRegex = /^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$/;
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

const Register = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    key: "",
  });

  const [validData, setValidData] = useState({
    username: false,
    email: false,
    password: false,
    confirmPassword: false,
    key: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errMsg, setErrMsg] = useState("");

  const formatKey = (value) => {
    value = value.replace(/[^a-zA-Z0-9]/g, "").slice(0, 16);
    return value.match(/.{1,4}/g)?.join("-") || value;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "key" ? formatKey(value) : value,
    }));
  };

  useEffect(() => {
    setValidData({
      username: userRegex.test(formData.username),
      email: emailRegex.test(formData.email),
      password: passwordRegex.test(formData.password),
      confirmPassword: formData.password === formData.confirmPassword,
      key: keyRegex.test(formData.key),
    });
    setErrMsg("");
  }, [formData]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!Object.values(validData).every(Boolean)) {
      setErrMsg("Please correct the errors before submitting.");
      return;
    }

    try {
      await registerUser(formData);
      navigate("/");
    } catch (error) {
      setErrMsg(error || "Registration failed. Please try again.");
    }
  };

  return (
    <div className="register-content">
      <h1>Register</h1>
      {errMsg && <p className="errmsg">{errMsg}</p>}
      <form onSubmit={handleSubmit}>
        <label>Username:</label>
        <div className="input-container">
          <input type="text" name="username" value={formData.username} onChange={handleChange} required />
          {validData.username ? <FaCheck className="valid" /> : <FaTimes className="invalid" />}
        </div>
        {!validData.username && formData.username && <p className="error-text"><FaInfoCircle /> 4-24 characters, must start with a letter.</p>}

        <label>Email:</label>
        <div className="input-container">
          <input type="email" name="email" value={formData.email} onChange={handleChange} required />
          {validData.email ? <FaCheck className="valid" /> : <FaTimes className="invalid" />}
        </div>
        {!validData.email && formData.email && <p className="error-text"><FaInfoCircle /> Must be a valid email format.</p>}

        <label>Password:</label>
        <div className="input-container">
          <input type={showPassword ? "text" : "password"} name="password" value={formData.password} onChange={handleChange} required />
          <span className="toggle-icon" onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
          {validData.password ? <FaCheck className="valid" /> : <FaTimes className="invalid" />}
        </div>
        {!validData.password && formData.password && <p className="error-text"><FaInfoCircle /> Must contain upper, lower, number, and special (!@#$%).</p>}

        <label>Confirm Password:</label>
        <div className="input-container">
          <input type={showConfirmPassword ? "text" : "password"} name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} required />
          <span className="toggle-icon" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
          {validData.confirmPassword ? <FaCheck className="valid" /> : <FaTimes className="invalid" />}
        </div>
        {!validData.confirmPassword && formData.confirmPassword && <p className="error-text"><FaInfoCircle /> Passwords must match.</p>}

        <label>Registration Key:</label>
        <div className="input-container">
          <input type="text" name="key" value={formData.key} onChange={handleChange} required />
          {validData.key ? <FaCheck className="valid" /> : <FaTimes className="invalid" />}
        </div>
        {!validData.key && formData.key && <p className="error-text"><FaInfoCircle /> Format: XXXX-XXXX-XXXX-XXXX</p>}

        <button type="submit" className={`register-button br-${Object.values(validData).every(Boolean)}`} disabled={!Object.values(validData).every(Boolean)}>Sign Up</button>
      </form>
      <p>
        Already have an account? <span className="link" onClick={() => navigate("/login")}>Login now!</span>
      </p>
    </div>
  );
};

export default Register;
