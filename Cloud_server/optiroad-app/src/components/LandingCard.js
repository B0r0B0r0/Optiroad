import React from "react";
import "../assets/styles/LandingCard.css";
import { useNavigate } from "react-router-dom";

const LandingCard = () => {
  const navigate = useNavigate();
  

  return (
    <div className="card-container">
      <h1 className="card-title">Welcome to OptiRoad</h1>
      <h2 className="card-subtitle">Revolutionizing Traffic in Intelligent Cities</h2>

      <p className="card-text">
        At OptiRoad, we leverage cutting-edge technology to create smarter traffic solutions for modern cities. 
        Join us in transforming urban mobility and making cities more efficient and enjoyable to live in.
      </p>

      <p className="card-text">
        You need to be logged in to access our services. Please contact an administrator for a registration key and make your city great today!
      </p>

      <div className="card-buttons">
        <div className="button-group">
          <p className="bluetext">Make your city great today!</p>
          <button className="button-login" onClick={() => navigate("/register")}>
            Register
          </button>
        </div>
        <div className="button-group">
          <p className="bluetext">If you already have an account</p>
          <button className="button-login" onClick={() => navigate("/login")}>
            Login
          </button>
        </div>
      </div>

      <p className="card-footer">
        Together, we can build the future of urban mobility. Contact us today to learn more about our innovative solutions.
      </p>

      <div className="card-bottom-links">
        <a className="bluetext bottom-link" onClick={(e) => { e.preventDefault(); navigate("/about"); }}>
          I would like to learn more about OptiRoad
        </a>
        <a className="bluetext bottom-link" onClick={(e) => { e.preventDefault(); navigate("/contact"); }}>
          I would like to contact an administrator!
        </a>
      </div>
    </div>
  );
};

export default LandingCard;
