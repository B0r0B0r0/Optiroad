import React, {useContext, useEffect, useState} from "react";
import { useNavigate, useLocation } from "react-router-dom";
import BackgroundVideo from "../components/BackgroundVideo";
import LandingCard from "../components/LandingCard";
import Register from "../components/Register";
import Login from "../components/Login";
import About from "../components/About"
import Contact from "../components/Contact"
import RequestKey from "../components/RequestKey";
import PrivacyPolicy from "../components/PrivacyPolicy";
import TermsOfUse from "../components/TermsOfUse";
import "../assets/styles/Homepage.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";
import AddCity from "./AddCity";

const Homepage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const { user } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    } else {
      setLoading(false); 
    }
  }, [user, navigate]);

  if (loading) return null; 

  return (
  <>
    <Navbar />
    <div className="homepage-container">
      <BackgroundVideo />
      <div className="overlay-content">
        {location.pathname === "/register" ? <Register /> : 
         location.pathname === "/login" ? <Login /> : 
         location.pathname === "/about" ? <About /> :
         location.pathname === "/contact" ? <Contact />:
         location.pathname === "/request-key" ? <RequestKey /> :
         location.pathname === "/privacy-policy" ? <PrivacyPolicy /> :
         location.pathname === "/terms-of-use" ? <TermsOfUse /> :
         <LandingCard navigate={navigate} />}
      </div>
    </div>
<Footer />
    </>
  );
};

export default Homepage;
