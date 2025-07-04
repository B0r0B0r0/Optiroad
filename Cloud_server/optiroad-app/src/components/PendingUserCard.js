import React, { use } from "react";
import "../assets/styles/PendingUserCard.css";
import { denyUser, approveUser } from "../services/userService";

const PendingUserCard = ({ user, reloadUsers }) => {


  const handleApprove = async () => {
    try {
      const response = await approveUser(user.id, user.first_name, user.last_name, user.email)
      reloadUsers();
    } catch (error) {
      console.error("Error approving user:", error);
     }
  }

  const handleDeny = async () => {
    try {
      const response = await denyUser(user.id, user.id_front, user.id_back, user.first_name, user.last_name, user.email);
      reloadUsers();
    } catch (error) {
      console.error("Error denying user:", error);
    }
  }

  return (
    <div className="pending-user-card">
      <div className="pending-user-header">
        <h2>{user.first_name} {user.last_name}</h2>
        <p className="pending-user-email">{user.email}</p>
      </div>

      <div className="pending-user-details">
        <p><strong>Address:</strong> {user.address}</p>
        <p><strong>Birth Date:</strong> {user.date_of_birth}</p>
        <p><strong>Profession:</strong> {user.profession}</p>
        <p><strong>WorkPlace:</strong> {user.workplace}</p>
        <p><strong>Phone:</strong> {user.phone}</p>
        <p><strong>Solicited at:</strong> {new Date(user.created_at).toLocaleString()}</p>
      </div>

      <div className="pending-user-images">
        <div>
          <p><strong>ID Card Front:</strong></p>
          <img src={user.id_front} alt="ID Front" className="user-id-image" />
        </div>
        <div>
          <p><strong>ID Card Back:</strong></p>
          <img src={user.id_back} alt="ID Back" className="user-id-image" />
        </div>
      </div>

      <div className="pending-user-actions">
        <button className="deny-button" onClick={handleDeny}>Deny</button>
        <button className="approve-button" onClick={handleApprove}>Approve</button>
      </div>
    </div>
  );
};

export default PendingUserCard;
