import React, { useContext, useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import AuthContext from "../context/AuthContext";
import { changePassword } from "../services/authService";
import {
  FaLock,
  FaSave,
  FaEye,
  FaEyeSlash,
  FaCheck,
  FaTimes,
  FaInfoCircle,
} from "react-icons/fa";
import "../assets/styles/AccountSettings.css";

const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;

const AccountSettings = () => {

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [validNew, setValidNew] = useState(false);
  const [validConfirm, setValidConfirm] = useState(false);

  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    setValidNew(passwordRegex.test(newPassword));
    setValidConfirm(newPassword === confirmPassword && confirmPassword.length > 0);
  }, [newPassword, confirmPassword]);

  const handleChangePassword = async () => {
    setError("");
    setSuccess("");

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (!validNew || !validConfirm) {
      setError("Please fix validation errors.");
      return;
    }

    try {
      await changePassword({
        oldPassword,
        newPassword,
      });
      setSuccess("Password changed successfully!");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="settings-container">
        <h1 className="dashboard-title">Account Settings</h1>

        <div className="login-content">
          <h2>
            <FaLock /> Change Password
          </h2>

          {error && <p className="error-text">{error}</p>}
          {success && <p className="valid">{success}</p>}

          <label>Current Password</label>
          <div className="input-container">
            <input
              type={showOld ? "text" : "password"}
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
            />
            <span className="toggle-icon-login" onClick={() => setShowOld(!showOld)}>
              {showOld ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          <label>New Password</label>
          <div className="input-container">
            <input
              type={showNew ? "text" : "password"}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <span className="toggle-icon-login" onClick={() => setShowNew(!showNew)}>
              {showNew ? <FaEyeSlash /> : <FaEye />}
            </span>
            {newPassword && (validNew ? <FaCheck className="valid" /> : <FaTimes className="invalid" />)}
          </div>
          {!validNew && newPassword && (
            <p className="error-text">
              <FaInfoCircle /> Must contain upper, lower, number, and special (!@#$%), 8–24 characters.
            </p>
          )}

          <label>Confirm New Password</label>
          <div className="input-container">
            <input
              type={showConfirm ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <span className="toggle-icon-login" onClick={() => setShowConfirm(!showConfirm)}>
              {showConfirm ? <FaEyeSlash /> : <FaEye />}
            </span>
            {confirmPassword && (validConfirm ? <FaCheck className="valid" /> : <FaTimes className="invalid" />)}
          </div>
          {!validConfirm && confirmPassword && (
            <p className="error-text">
              <FaInfoCircle /> Passwords must match.
            </p>
          )}

          <button
            className={`login-button bl-${oldPassword && validNew && validConfirm}`}
            onClick={handleChangePassword}
            disabled={!(oldPassword && validNew && validConfirm)}
          >
            <FaSave /> Update Password
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountSettings;
