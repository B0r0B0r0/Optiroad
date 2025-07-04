import React from "react";
import { FaCheckSquare ,FaMapMarkerAlt, FaEnvelope, FaPhone, FaRoad, FaCity, FaLightbulb, FaTools } from "react-icons/fa";
import "../assets/styles/About.css";

const About = () => {
  return (
    <div className="about-content">
      <h1>About OptiRoad</h1>
      <p>
        <strong>OptiRoad</strong> is an innovative smart traffic management system designed to revolutionize urban mobility.
        We leverage <strong>AI-powered algorithms</strong> and <strong>real-time data analysis</strong> to optimize traffic flow, reduce congestion,
        and enhance road safety.
      </p>

      <h2><FaLightbulb /> Our Vision</h2>
      <p>
        Our mission is to create <strong>intelligent, self-adapting urban traffic solutions</strong> that improve efficiency and 
        sustainability. We aim to <strong>eliminate unnecessary delays</strong>, reduce carbon emissions, and 
        enhance the driving experience for millions of people.
      </p>

      <h2><FaRoad /> How OptiRoad Works</h2>
      <p>
        OptiRoad integrates <strong>computer vision, AI-based traffic pattern recognition, and IoT-connected infrastructure </strong> 
        to provide a cutting-edge traffic management system. Our <strong>real-time analytics</strong> help cities and road authorities make 
        better decisions by predicting congestion, identifying bottlenecks, and suggesting alternate routes.
      </p>

      <h2><FaCity /> Who Can Benefit?</h2>
      <p>
        - <strong>City Administrations:</strong> Optimize traffic signals and reduce congestion in real-time. <br />
        - <strong>Logistics & Transport Companies:</strong> Get real-time route optimizations to improve delivery times. <br />
        - <strong>Commuters & Drivers:</strong> Reduce waiting time at intersections and get AI-driven route suggestions.
      </p>

      <h2><FaTools /> Key Features</h2>
      <ul className="feature-list">
        <li><FaCheckSquare className="check-icon" /><div><strong>AI-powered real-time traffic monitoring</strong></div></li>
        <li><FaCheckSquare className="check-icon" /><div><strong>Predictive analytics</strong> to prevent congestion</div></li>
        <li><FaCheckSquare className="check-icon" /><div><strong>Seamless integration</strong> with smart city infrastructure</div></li>
        <li><FaCheckSquare className="check-icon" /><div><strong>Automated emergency lane detection</strong> for first responders</div></li>
        <li><FaCheckSquare className="check-icon" /><div><strong>Privacy-focused data collection</strong> with encrypted storage</div></li>
      </ul>

      <h2>Contact Us</h2>
      <p>
        <FaMapMarkerAlt /> <strong>Location:</strong> Military Technical Academy, Bucharest, Romania<br />
        <FaEnvelope /> <strong>Email:</strong> <a style={{cursor: "pointer"}} href="mailto:support@optiroad.com">support@optiroad.com</a><br />
        <FaPhone /> <strong>Phone:</strong> +40 768 158 293
      </p>
    </div>
  );
};

export default About;
