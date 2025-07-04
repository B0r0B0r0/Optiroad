import React from "react";
import { Link } from "react-router-dom";
import "../assets/styles/Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>&copy; {new Date().getFullYear()} OptiRoad. All rights reserved.</p>
        <div className="footer-links">
          <Link to="/about" className="footer-button">About</Link>
          <Link to="/contact" className="footer-button">Contact</Link>
          <Link to="/privacy-policy" className="footer-button">Privacy Policy</Link>
          <Link to="/terms-of-use" className="footer-button">Terms of Use</Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
