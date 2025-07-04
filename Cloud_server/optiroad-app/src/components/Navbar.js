import React from "react";
import { Link, useLocation } from "react-router-dom";
import "../assets/styles/Navbar.css";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/">OptiRoad</Link>
      </div>
      <ul className="navbar-links">
        <li><Link to="/" className={`nav-button ${location.pathname === "/" ? "active" : ""}`}>Home</Link></li>
        <li><Link to="/about" className={`nav-button ${location.pathname === "/about" ? "active" : ""}`}>About</Link></li>
        <li><Link to="/login" className={`nav-button ${location.pathname === "/login" ? "active" : ""}`}>Login</Link></li>
        <li><Link to="/register" className={`nav-button ${location.pathname === "/register" ? "active" : ""}`}>Register</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;
