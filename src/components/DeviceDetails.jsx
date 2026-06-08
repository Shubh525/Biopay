import React, { useState, useEffect } from "react";
import axios from "axios";
import "./DeviceDetails.css";
import bgVideo from "../assets/images/login.mp4"; // reuse same background video

const DeviceDetails = () => {
  const [device, setDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
useEffect(() => {
  const fetchDevice = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/device/status");
      setDevice(res.data);
    } catch (err) {
      console.error("Error fetching device details:", err);
      setError("Unable to fetch device details. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  fetchDevice();
  const interval = setInterval(fetchDevice, 4000); // Refresh every 4 seconds
  return () => clearInterval(interval);
}, []);

  return (
    <div className="device-container">
      <video className="device-background-video" autoPlay loop muted playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>

      <div className="device-overlay">
        <div className="device-card">
          <h2 className="device-title">Palm Vein Device Details</h2>

          {loading ? (
            <p className="device-status">Loading device information...</p>
          ) : error ? (
            <p className="device-error">{error}</p>
          ) : device ? (
            <div className="device-info">
              <p><strong>Device Name:</strong> {device.name || "PalmSecure Sensor"}</p>
              <p><strong>Device ID:</strong> {device.id || "N/A"}</p>
              <p><strong>Firmware Version:</strong> {device.firmware || "1.0.0"}</p>
              <p><strong>Connection Status:</strong> 
                <span className={`status ${device.connected ? "connected" : "disconnected"}`}>
                  {device.connected ? "Connected" : "Disconnected"}
                </span>
              </p>
              <p><strong>Last Checked:</strong> {new Date().toLocaleString()}</p>
            </div>
          ) : (
            <p className="device-error">No device data available.</p>
          )}

          <button className="btn-refresh" onClick={() => window.location.reload()}>
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeviceDetails;
