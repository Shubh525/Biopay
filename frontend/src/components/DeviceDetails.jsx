import React, { useState, useEffect } from "react";
import axios from "axios";
import "./DeviceDetails.css";
import API_BASE from '../api.js';

const DeviceDetails = () => {
  const [device, setDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const DEVICE_API = `${API_BASE}/api/device/status`;
  const handleRefresh = async () => {
    setLoading(true);

    try {
      const res = await axios.get(
        DEVICE_API,
        {
          timeout: 5000,
        }
      );

      setDevice(res.data);
      setError("");
    } catch {
      setError(
        "Unable to fetch device details. Please check your connection."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    const fetchDevice = async () => {
      try {
        const res = await axios.get(
          DEVICE_API,
          {
            timeout: 5000,
          }
        );

        if (isMounted) {
          setDevice(res.data);
          setError("");
        }
      } catch (err) {
        console.error("Error fetching device details:", err);
        if (isMounted) {
          setError("Unable to fetch device details. Please check your connection.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchDevice();
    const interval = setInterval(fetchDevice, 4000); // Refresh every 4 seconds
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="device-container">
      <video
        className="device-background-video"
        autoPlay
        loop
        muted
        playsInline
        preload="metadata"
      >
        <source src="/videos/login.mp4" type="video/mp4" />
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
                <span
                  className={`status ${Boolean(device.connected)
                    ? "connected"
                    : "disconnected"
                    }`}
                >
                  {Boolean(device.connected)
                    ? "Connected"
                    : "Disconnected"}
                </span>
              </p>
              <p><strong>Last Checked:</strong> {new Date().toLocaleString()}</p>
            </div>
          ) : (
            <p className="device-error">No device data available.</p>
          )}

          <button
            className="btn-refresh"
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeviceDetails;
