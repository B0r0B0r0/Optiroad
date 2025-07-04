import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import { loginUser } from "../services/authService";
import "../assets/styles/Login.css";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [errMsg, setErrMsg] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.username || !formData.password) {
      setErrMsg("Please enter your username and password.");
      return;
    }

    try {
      await login(formData);
      navigate("/dashboard"); 
    } catch (error) {
      setErrMsg(error.message);
    }
  };

  return (
    <div className="login-content">
      <h1>Login</h1>
      {errMsg && <p className="errmsg">{errMsg}</p>}
      <form onSubmit={handleSubmit}>
        <label>Username:</label>
        <div className="input-container">
          <input type="text" name="username" value={formData.username} onChange={handleChange} required />
        </div>

        <label>Password:</label>
        <div className="input-container">
          <input type={showPassword ? "text" : "password"} name="password" value={formData.password} onChange={handleChange} required />
          <span className="toggle-icon-login" onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
        </div>

        <button type="submit" className={`login-button bl-${(formData.username && formData.password) ? true : false}`} disabled={!(formData.username && formData.password)}>Login</button>
      </form>
      <p>
        Don't have an account? <span className="link" onClick={() => navigate("/register")}>Register now!</span>
      </p>
    </div>
  );
};

export default Login;
