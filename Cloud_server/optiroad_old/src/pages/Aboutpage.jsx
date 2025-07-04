import React from "react";
import "./aboutpage.css";

const AboutUs = () => {
  return (
    <div className="about-container">
      <div className="about-content">
        <h1 className="about-title">About OptiRoad</h1>
        <p className="about-text">
          OptiRoad is an innovative smart traffic control system designed to optimize urban traffic 
          and reduce congestion through artificial intelligence, real-time monitoring, and data-driven 
          decision-making. By integrating edge devices, surveillance cameras, and a cloud-based 
          analytical platform, OptiRoad ensures better traffic flow and improved road safety.
        </p>
        <h2 className="about-subtitle">Our Mission</h2>
        <p className="about-text">
          Our mission is to revolutionize traffic management in smart cities by leveraging cutting-edge 
          AI and IoT technologies. We aim to enhance urban mobility, reduce carbon emissions, and 
          improve overall transportation efficiency.
        </p>
        <h2 className="about-subtitle">Core Objectives</h2>
        <ul className="about-list">
          <li>Real-time traffic monitoring using AI-powered analytics.</li>
          <li>Dynamic traffic light optimization to reduce congestion.</li>
          <li>Secure and scalable cloud-based data processing.</li>
          <li>Intelligent route recommendations for drivers.</li>
          <li>Seamless integration with municipal traffic management systems.</li>
        </ul>
        <h2 className="about-subtitle">Why OptiRoad?</h2>
        <p className="about-text">
          Unlike traditional traffic management systems, OptiRoad harnesses the power of AI and 
          real-time data collection to adapt dynamically to urban traffic conditions. By using 
          computer vision and machine learning, we can predict congestion patterns and optimize 
          traffic flow to make our cities smarter and more efficient.
        </p>
      </div>
    </div>
  );
};

export default AboutUs;
