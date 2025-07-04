import React from "react";
import { useNavigate } from "react-router-dom";
import { FaVideo, FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import "../assets/styles/CityCard.css";
import { getCityCoordinates } from "../services/cityService"; // ajustează calea dacă e diferită

const CityCard = ({ city }) => {
  const navigate = useNavigate();

  const handleClick = async () => {
    // Salvăm metadatele orașului
    localStorage.setItem(`city:${city.name.toLowerCase()}`, JSON.stringify({
      name: city.name,
      county: city.county,
      country: city.country
    }));

    // Cerem coordonatele de la backend
    const response = await getCityCoordinates({
      country: city.country,
      county: city.county,
      city: city.name
    });

    if (response.error) {
      console.error("Eroare la obținerea coordonatelor:", response.error);
      return;
    }

    // Salvăm coordonatele în localStorage
    localStorage.setItem(`city:coords:${city.name.toLowerCase()}`, JSON.stringify({
      lat: response.lat,
      lon: response.lon
    }));

    // Navigăm către pagina orașului
    navigate(`/city/${city.name.toLowerCase()}`);
  };

  return (
    <div className="city-card" onClick={handleClick}>
      <div className="city-info">
        <h2>{city.name}</h2>
        <p><FaVideo className="icon" /> Cameras: {city.cameras}</p>
        <p>
          <FaCheckCircle className="icon green" /> Online: {city.online} 
          <FaTimesCircle className="icon red" /> Offline: {city.offline}
        </p>
      </div>
    </div>
  );
};

export default CityCard;
