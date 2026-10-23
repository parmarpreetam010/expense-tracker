import { useState, useEffect } from "react";
import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedEmail = localStorage.getItem("userEmail");
    if (savedToken) {
      setToken(savedToken);
      setUserEmail(savedEmail || "User");
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    setToken(null);
    setUserEmail("");
  };

  if (!token) {
    return (
      <Auth
        onLoginSuccess={(newToken) => {
          setToken(newToken);
          setUserEmail(localStorage.getItem("userEmail") || "User");
        }}
      />
    );
  }

  return <Dashboard userEmail={userEmail} onLogout={handleLogout} />;
}