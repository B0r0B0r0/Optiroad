import React from "react";
import { FaGavel, FaUserShield, FaExclamationTriangle, FaHandshake, FaBan } from "react-icons/fa";
import "../assets/styles/TermsOfUse.css";

const TermsOfUse = () => {
  return (
    <div className="terms-of-use-content">
      <h1>Terms of Use</h1>
      <p>Last updated: <strong>March 2025</strong></p>

      <h2><FaGavel /> Acceptance of Terms</h2>
      <p>
        By accessing and using <strong>OptiRoad</strong>, you agree to be bound by these Terms of Use.
        If you do not agree, you must not use our services.
      </p>

      <h2><FaUserShield /> User Responsibilities</h2>
      <ul className="terms-list">
        <li>
            <FaExclamationTriangle className="icon" />
            <div>You must provide accurate and truthful information when registering.</div>
        </li>
        <li>
            <FaExclamationTriangle className="icon" />
            <div>You are responsible for maintaining the security of your account.</div>
        </li>
        <li>
            <FaExclamationTriangle className="icon" />
            <div>Any misuse of the platform, including fraud or abuse, is strictly prohibited.</div>
        </li>
      </ul>

    <h2><FaBan /> Prohibited Activities</h2>
    <ul className="terms-list">
    <li>
        <FaBan className="icon" />
        <div>Attempting to hack, manipulate, or exploit system vulnerabilities.</div>
    </li>
    <li>
        <FaBan className="icon" />
        <div>Using our platform for illegal or unauthorized purposes.</div>
    </li>
    <li>
        <FaBan className="icon" />
        <div>Sharing or distributing false information.</div>
    </li>
    </ul>

      <h2><FaHandshake /> Changes to Terms</h2>
      <p>
        We reserve the right to update these Terms at any time. Your continued use of the platform constitutes acceptance of any modifications.
      </p>

      <h2>Contact Us</h2>
      <p>If you have any questions, contact us at:</p>
      <p><strong>Email:</strong> <a href="mailto:support@optiroad.com">support@optiroad.com</a></p>
    </div>
  );
};

export default TermsOfUse;
