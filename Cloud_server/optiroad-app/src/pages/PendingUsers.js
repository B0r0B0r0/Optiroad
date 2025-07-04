import React, { useEffect, useState } from "react";
import { getPendingUsers } from "../services/userService";
import "../assets/styles/PendingUsers.css";
import Sidebar from "../components/Sidebar";
import PendingUserCard from "../components/PendingUserCard";

const PendingUsers = () => {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);

const loadUsers = async () => {
    try {
      const data = await getPendingUsers();
      const arrayified = Object.entries(data.users).map(([id, user]) => ({
        id,
        ...user
      }));
      setPendingUsers(arrayified);
    } catch (err) {
      console.error("Eroare la fetch:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);


 return (
    <div className="pending-container">
      <Sidebar />
      <h1 className="dashboard-title">Pending users</h1>
      {loading ? (
        <p className="pending-loading">Loading...</p>
      ) : pendingUsers.length === 0 ? (
        <p className="pending-empty">No users waiting for approval.</p>
      ) : (
        <div className="pending-user-list">
          {pendingUsers.map((user) => (
            <PendingUserCard key={user.id} user={user} reloadUsers={loadUsers}/>
          ))}
        </div>
      )}
    </div>
  );
};

export default PendingUsers;