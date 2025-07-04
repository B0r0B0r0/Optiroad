import React from "react";
import "../assets/styles/Dashboard.css";
import Sidebar from "../components/Sidebar";
import CityList from "../components/CityList";
import { useAuth } from "../context/AuthContext";

const Dashboard = () => {
   const { user, logout } = useAuth();
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-content">
        <h1 className="dashboard-title">
          Welcome, {user ? user.username : "Guest"}! <br/>
          Configured Cities
        </h1>
        <CityList />
      </div>
    </div>
  );
};

export default Dashboard;
