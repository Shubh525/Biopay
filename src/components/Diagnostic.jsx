import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Diagnostic.css";
import bgVideo from "../assets/images/login.mp4";

import API_BASE from '../api.js';

const DEVICE_API = `${API_BASE}/api/device/status`;
const DIAGNOSTIC_API = `${API_BASE}/api/diagnostics/run`;
const Diagnostic = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [diagnosticResults, setDiagnosticResults] = useState(null);
  const [diagnosticLoading, setDiagnosticLoading] = useState(false);

  // Fetch connected PalmSecure device(s)
  const fetchDevices = async () => {
    try {
      setLoading(true);
      setDiagnosticResults(null);
      const res = await axios.get(
        DEVICE_API,
        {
          timeout: 5000,
        }
      );
      if (res.data && res.data.connected) {
        setDevices([
          {
            manufacturer: "Fujitsu Frontech",
            product: res.data.name || "PalmSecure Sensor",
            serial_number: res.data.id || "Unknown",
          },
        ]);
      } else {
        setDevices([]);
      }
    } catch (err) {
      console.error("Error fetching devices:", err);

      setDevices([]);
      setDiagnosticResults(null);
    } finally {
      setLoading(false);
    }
  };

  // Run full system diagnostics
  const handleRunDiagnostics = async () => {
    if (diagnosticLoading) return;
    setDiagnosticLoading(true);
    setDiagnosticResults(null);

    try {
      const res = await axios.get(
        DIAGNOSTIC_API,
        {
          timeout: 10000,
        }
      );
      setDiagnosticResults(res.data || {});
    } catch (err) {
      console.error("Diagnostics failed:", err);

      setDiagnosticResults({
        error: "Unable to run diagnostics. Please check backend logs.",
      });

      setDevices([]);
    } finally {
      setDiagnosticLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadDevices = async () => {
      try {
        setLoading(true);

        const res = await axios.get(
          DEVICE_API,
          {
            timeout: 5000,
          }
        );

        if (!isMounted) return;

        if (res.data && res.data.connected) {
          setDevices([
            {
              manufacturer: "Fujitsu Frontech",
              product: res.data.name || "PalmSecure Sensor",
              serial_number: res.data.id || "Unknown",
            },
          ]);
        } else {
          setDevices([]);
        }
      } catch (err) {
        if (isMounted) {
          setDevices([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadDevices();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="diagnostic-container">
      <video
        className="diagnostic-background-video"
        autoPlay
        loop
        muted
        playsInline
        preload="metadata"
      >
        <source src={bgVideo} type="video/mp4" />
      </video>

      <div className="diagnostic-overlay">
        <div className="diagnostic-card">
          <h2 className="diagnostic-title">Device Diagnostics</h2>

          {/* ===== Available Devices ===== */}
          <div className="diagnostic-section">
            <div className="diagnostic-header">
              <h3>Available Devices</h3>
              <button
                className="btn-refresh"
                onClick={fetchDevices}
                disabled={loading || diagnosticLoading}
              >
                {loading ? "Scanning..." : "🔄 Refresh"}
              </button>
            </div>

            {loading ? (
              <div className="diagnostic-loading">
                <div className="spinner"></div>
                <p>Searching for connected devices...</p>
              </div>
            ) : devices.length > 0 ? (
              <table className="diagnostic-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Manufacturer</th>
                    <th>Product</th>
                    <th>Serial Number</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.map((device, index) => (
                    <tr key={device.serial_number || index}>
                      <td>{index + 1}</td>
                      <td>{device.manufacturer}</td>
                      <td>{device.product}</td>
                      <td>{device.serial_number}</td>
                      <td>
                        <button className="btn-connect">Connect</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="no-devices">
                <p className="emoji">🖐️</p>
                <h4>No PalmSecure Devices Found</h4>
                <p>Connect your device and click Refresh</p>
              </div>
            )}
          </div>

          {/* ===== Device Information ===== */}
          <div className="diagnostic-section">
            <h3>Device Information</h3>
            <div className="diagnostic-info">
              <div>
                <p><strong>Device:</strong> PalmSecure Sensor</p>
                <p><strong>USB VID:</strong> 0x04C5</p>
                <p><strong>USB PID:</strong> 0x125A</p>
                <p><strong>Manufacturer:</strong> FUJITSU FRONTECH LIMITED</p>
              </div>
              <div>
                <p><strong>Compatible Drivers:</strong></p>
                <ul>
                  <li>Version 3.1.6.3 (2013)</li>
                  <li>Version 3.1.7.4 (2017)</li>
                  <li>Version 3.2.0.1 (2022)</li>
                </ul>
              </div>
            </div>

            <div className="text-center">
              <button
                className="btn-run-diagnostics"
                onClick={handleRunDiagnostics}
                disabled={diagnosticLoading}
              >
                {diagnosticLoading ? "⏳ Running..." : "⚙️ Run Diagnostics"}
              </button>
            </div>

            {/* ===== Diagnostic Results ===== */}
            {diagnosticResults && (
              <div className="diagnostic-results mt-4">
                {diagnosticResults.error ? (
                  <p className="error-text">❌ {diagnosticResults.error}</p>
                ) : (
                  <>
                    <ul>
                      <li className={diagnosticResults.usb_subsystem === "OK" ? "ok" : "fail"}>
                        {diagnosticResults.usb_subsystem === "OK" ? "✅" : "❌"} USB Subsystem
                      </li>
                      <li className={diagnosticResults.driver_status === "OK" ? "ok" : "fail"}>
                        {diagnosticResults.driver_status === "OK" ? "✅" : "❌"} Driver Installed
                      </li>
                      <li className={diagnosticResults.permissions === "OK" ? "ok" : "fail"}>
                        {diagnosticResults.permissions === "OK" ? "✅" : "❌"} Permissions
                      </li>
                      <li className={diagnosticResults.device_detection === "OK" ? "ok" : "fail"}>
                        {diagnosticResults.device_detection === "OK" ? "✅" : "❌"} Device Detection
                      </li>
                      <li className={diagnosticResults.network === "OK" ? "ok" : "fail"}>
                        {diagnosticResults.network === "OK" ? "✅" : "❌"} Network
                      </li>
                    </ul>

                    <div className="diagnostic-summary">
                      <p>
                        <strong>Status:</strong>{" "}
                        {diagnosticResults.ready ? "✅ System Ready" : "⚠️ Issues Detected"}
                      </p>
                      <p>{diagnosticResults.message}</p>

                      {Array.isArray(diagnosticResults.issues) &&
                        diagnosticResults.issues.length > 0 && (
                          <>
                            <strong>Issues:</strong>
                            <ul>
                              {diagnosticResults.issues.map((issue, idx) => (
                                <li key={idx} className="fail">⚠️ {issue}</li>
                              ))}
                            </ul>
                          </>
                        )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Diagnostic;
