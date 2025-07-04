import React from "react";
import { useNavigate } from "react-router-dom";
import { FaHome, FaUserCog, FaSignOutAlt, FaCity } from "react-icons/fa";
import "../assets/styles/Sidebar.css";
import logo from "../assets/images/logo192.png";
import { useAuth } from "../context/AuthContext";

const Sidebar = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const navLinks = [
    { label: "Dashboard", icon: <FaHome className="sidebar-icon" />, path: "/dashboard", roles: ["admin", "maintainer"] },
    { label: "Register City", icon: <FaCity className="sidebar-icon" />, path: "/register-city", roles: ["admin", "maintainer"] },
    { label: "Account Settings", icon: <FaUserCog className="sidebar-icon" />, path: "/accSettings", roles: ["admin", "maintainer"] },
    { label: "Pending Users", icon: <FaUserCog className="sidebar-icon" />, path: "/pending-users", roles: ["admin"] },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-title">
        <img src={logo} alt="Optiroad Logo" className="sidebar-logo" />
        <span className="sidebar-title-text">Optiroad</span>
      </div>

      <div className="sidebar-nav">
        {navLinks
          .filter(link => link.roles.includes(user?.role))
          .map((link) => (
            <button
              key={link.path}
              className="sidebar-button"
              onClick={() => navigate(link.path)}
            >
              {link.icon} {link.label}
            </button>
          ))}
      </div>

      <div className="sidebar-bottom">
        <button className="sidebar-button logout" onClick={logout}>
          <FaSignOutAlt className="sidebar-icon" /> Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
