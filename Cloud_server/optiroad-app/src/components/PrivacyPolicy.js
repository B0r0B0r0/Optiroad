import React from "react";
import { FaUser, FaLock, FaShieldAlt, FaEye, FaEnvelope, FaGavel, FaCheckSquare, FaUserShield } from "react-icons/fa";
import "../assets/styles/PrivacyPolicy.css";

const PrivacyPolicy = () => {
  return (
    <div className="privacy-policy-content">
      <h1>Privacy Policy</h1>
      <p>Last updated: <strong>March 2025</strong></p>

      <h2><FaUser /> Introduction</h2>
      <p>
        At <strong>OptiRoad</strong>, we are committed to protecting your privacy and ensuring the security of your personal data. 
        This Privacy Policy explains how we collect, use, and safeguard your information.
      </p>

      <h2><FaLock /> Information We Collect</h2>
      <p>We may collect and process the following types of personal data:</p>
      <ul>
        <li><FaUser /> Personal details: Name, email, phone number, address.</li>
        <li><FaLock /> Account information: Username, password.</li>
        <li><FaShieldAlt /> Identification details: ID front and back images (for key request verification).</li>
        <li><FaEye /> Usage data: How you interact with our platform.</li>
      </ul>

      <h2><FaShieldAlt /> How We Use Your Information</h2>
      <p>We use your data for the following purposes:</p>
      <ul className="feature-list">
        <li><FaCheckSquare className="check-icon" /><div>To process your registration and provide access to our services.</div></li>
        <li><FaCheckSquare className="check-icon" /><div>To verify your identity for security purposes.</div></li>
        <li><FaCheckSquare className="check-icon" /><div>To improve our services based on user feedback.</div></li>
        <li><FaCheckSquare className="check-icon" /><div>To comply with legal requirements.</div></li>
      </ul>

      <h2><FaShieldAlt /> Data Security</h2>
      <p>
        We implement strict security measures to protect your data. All personal data is stored securely and encrypted where necessary.
      </p>

      <h2><FaGavel /> Sharing of Information</h2>
      <p>
        We do not sell or share your personal data with third parties, except when required by law.
      </p>

      <h2><FaUserShield /> Your Rights</h2>
      <p>You have the right to:</p>
      <ul className="feature-list">
        <li><FaCheckSquare className="check-icon" /><div>Access your personal data.</div></li>
        <li><FaCheckSquare className="check-icon" /><div>Request data correction or deletion.</div></li>
        <li><FaCheckSquare className="check-icon" /><div>Object to certain data processing activities.</div></li>
      </ul>

      <h2><FaEnvelope /> Contact Us</h2>
      <p>If you have any questions, you can contact us at:</p>
      <p><strong>Email:</strong> <a href="mailto:privacy@optiroad.com">privacy@optiroad.com</a></p>
    </div>
  );
};

export default PrivacyPolicy;
