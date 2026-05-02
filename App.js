import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [status, setStatus] = useState("Connecting...");

  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      setStatus(response.data.message || "Connected!");
      console.log(response.data.message);
    } catch (e) {
      setStatus("Backend not connected — running in standalone mode.");
      console.error(e, "errored out requesting / api");
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div>
      <header className="App-header">
        <h1 className="agency-title">JAI SARVALAYA</h1>
        <p className="agency-sub">— AGENCY —</p>
        <p className="agency-tagline">"Your Luck Begins Here"</p>
        <p className="status-text">API Status: {status}</p>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;

