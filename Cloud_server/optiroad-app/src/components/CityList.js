import React, { useEffect, useState } from "react";
import CityCard from "./CityCard";
import "../assets/styles/CityList.css";
import { getMyCities } from "../services/cityService";

const CityList = () => {
  const [cities, setCities] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const response = await getMyCities();

        if (Array.isArray(response)) {
          setCities(response);
        } else {
          console.warn("getMyCities did not return an array:", response);
          setCities([]);
        }
      } catch (err) {
        console.error("Failed to fetch cities:", err);
        setCities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCities();
  }, []);

  if (loading) return <div>Loading cities...</div>;

  return (
    <div className="city-list">
      {cities.map((city, index) => (
        <CityCard key={index} city={city} />
      ))}
    </div>
  );
};

export default CityList;
