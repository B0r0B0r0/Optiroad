import React from "react";
import "../assets/styles/BackgroundVideo.css";

const BackgroundVideo = () => {
  return (
    <div className="video-container">
      <video autoPlay loop muted disablePictureInPicture controlsList="nodownload nofullscreen noremoteplayback">
        <source src="/assets/videos/background.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <div className="video-overlay"></div> 
    </div>
  );
};

export default BackgroundVideo;
