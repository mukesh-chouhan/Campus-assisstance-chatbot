import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

const BACKEND_URL = "http://localhost:5000";

function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isAdminMode, setIsAdminMode] = useState(false);
  const navigate = useNavigate();

  // Email validation function
  const validateEmail = (email) => {
    if (isAdminMode) {
      // Admin can use any email
      return email.includes('@');
    }
    const emailRegex = /^[^\s@]+@iare\.ac\.in$/;
    return emailRegex.test(email);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!email || !password) {
      setErrorMessage("Please fill all fields");
      return;
    }

    if (!validateEmail(email)) {
      setErrorMessage(isAdminMode ? "Please enter a valid email" : "Please use college email address");
      return;
    }

    // Admin login check
    if (isAdminMode) {
      try {
        const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const data = await res.json();

        if (!res.ok) {
          setErrorMessage(data.error || "Invalid admin credentials");
          setIsLoading(false);
          return;
        }

        if (data.success && data.user.role === 'admin') {
          setSuccessMessage("Admin login successful! Redirecting...");
          localStorage.setItem('admin', JSON.stringify(data.user));
          setTimeout(() => {
            navigate("/admin");
          }, 1500);
        } else {
          setErrorMessage("Not authorized as admin");
        }
        setIsLoading(false);
        return;
      } catch (err) {
        setErrorMessage("Login failed. Please try again.");
        setIsLoading(false);
        return;
      }
    }

    setIsLoading(true);
    try {
      // Student login via SQLite backend
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      console.log("Login response:", data);

      if (!res.ok) {
        setErrorMessage(data.error || "Invalid email or password");
        setIsLoading(false);
        return;
      }

      if (data.success) {
        console.log("Login successful, saving user:", data.user);
        setSuccessMessage("Login successful! Redirecting...");
        localStorage.setItem('user', JSON.stringify(data.user));
        console.log("Navigating to /user");
        setTimeout(() => {
          navigate("/user");
        }, 1500);
      } else {
        setErrorMessage("Login failed. Please try again.");
      }
    } catch (err) {
      console.error("Authentication error:", err);
      setErrorMessage("Login failed. Server might be offline.");
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <>
      <style>
        {`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
          }
        `}
      </style>
      <div style={styles.container}>
        <form
          style={styles.form}
          onSubmit={handleLogin}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.02)";
            e.currentTarget.style.transition = "transform 0.3s ease";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
          }}
        >
          <div style={styles.logoContainer}>
            <div style={styles.logo}>🤖</div>
            <h2 style={styles.title}>Campus Assistant</h2>
            <p style={styles.tagline}>IARE Chatbot Portal</p>
          </div>

          {/* Mode Toggle */}
          <div style={styles.modeToggle}>
            <button
              type="button"
              style={{
                ...styles.toggleButton,
                ...((!isAdminMode) ? styles.toggleButtonActive : {})
              }}
              onClick={() => setIsAdminMode(false)}
            >
              Student Login
            </button>
            <button
              type="button"
              style={{
                ...styles.toggleButton,
                ...((isAdminMode) ? styles.toggleButtonActive : {})
              }}
              onClick={() => setIsAdminMode(true)}
            >
              Admin Login
            </button>
          </div>

          <input
            type="email"
            placeholder={isAdminMode ? "admin@iare.ac.in" : "username@iare.ac.in"}
            style={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <div style={styles.passwordWrapper}>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              style={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <span
              onClick={() => setShowPassword(!showPassword)}
              style={styles.eyeIcon}
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          {errorMessage && (
            <div style={styles.errorMessage}>
              {errorMessage}
            </div>
          )}

          {successMessage && (
            <div style={styles.successMessage}>
              {successMessage}
            </div>
          )}

          <button type="submit" style={styles.button} disabled={isLoading}>
            {isLoading ? "Logging in..." : (isAdminMode ? "Admin Login" : "Student Login")}
          </button>

          <div style={styles.linkText}>
            <Link to="/forgot-password" style={styles.link}>Forgot Password?</Link>
          </div>
        </form>
      </div>
    </>
  );
}

function HomePage() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      localStorage.removeItem('user');
      navigate("/");
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <div style={{ ...styles.container, backgroundColor: "#1b1b1b", color: "white" }}>
      <h1>Welcome Home 🎉</h1>
      <button onClick={handleLogout} style={styles.button}>
        Logout
      </button>
    </div>
  );
}


// Inline Styles
const styles = {
  container: {
    display: "flex",
    height: "100vh",
    width: "100vw",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #000 0%, #0a3d0a 50%, #00ff7f 100%)",
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    margin: 0,
    padding: 0,
    overflow: "hidden",
  },
  form: {
    backgroundColor: "rgba(0,0,0,0.9)",
    padding: "40px",
    borderRadius: "20px",
    boxShadow: "0px 0px 40px rgba(0,255,127,0.4)",
    border: "2px solid rgba(0,255,127,0.3)",
    width: "450px",
    textAlign: "center",
    minHeight: "550px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    backdropFilter: "blur(10px)",
  },
  logoContainer: {
    marginBottom: "30px",
  },
  logo: {
    fontSize: "4rem",
    marginBottom: "10px",
    filter: "drop-shadow(0 0 10px #00ff7f)",
  },
  tagline: {
    color: "#888",
    fontSize: "14px",
    marginTop: "5px",
  },
  modeToggle: {
    display: "flex",
    gap: "10px",
    marginBottom: "30px",
    background: "rgba(0,0,0,0.5)",
    padding: "5px",
    borderRadius: "10px",
  },
  toggleButton: {
    flex: 1,
    padding: "12px",
    background: "transparent",
    border: "none",
    color: "#888",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
    transition: "all 0.3s ease",
  },
  toggleButtonActive: {
    background: "linear-gradient(135deg, #00ff7f 0%, #00cc66 100%)",
    color: "#000",
    boxShadow: "0 4px 15px rgba(0,255,127,0.4)",
  },
  title: {
    color: "#00ff7f",
    marginBottom: "5px",
    fontSize: "28px",
    fontWeight: "bold",
    textShadow: "0 0 20px rgba(0,255,127,0.5)",
  },
  input: {
    width: "100%",
    padding: "15px",
    marginBottom: "20px",
    borderRadius: "10px",
    border: "2px solid rgba(0,255,127,0.3)",
    outline: "none",
    fontSize: "16px",
    backgroundColor: "rgba(0,255,127,0.05)",
    color: "white",
    transition: "all 0.3s ease",
  },
  button: {
    width: "100%",
    padding: "16px",
    background: "linear-gradient(135deg, #00ff7f 0%, #00cc66 100%)",
    color: "#000",
    fontWeight: "bold",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "18px",
    marginTop: "10px",
    transition: "all 0.3s ease",
    boxShadow: "0 6px 20px rgba(0,255,127,0.4)",
  },
  passwordWrapper: {
    position: "relative",
  },
  eyeIcon: {
    position: "absolute",
    right: "15px",
    top: "50%",
    transform: "translateY(-50%)",
    cursor: "pointer",
    color: "white",
    background: "rgba(0,0,0,0.5)",
    borderRadius: "50%",
    width: "32px",
    height: "32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "16px",
    transition: "background-color 0.3s ease",
    marginTop: "-10px",
  },
  linkText: {
    marginTop: "20px",
    color: "white",
    fontSize: "16px",
  },
  link: {
    color: "#00ff7f",
    textDecoration: "none",
    fontWeight: "bold",
  },
  errorMessage: {
    color: "#ff6b6b",
    backgroundColor: "rgba(255, 107, 107, 0.15)",
    padding: "15px",
    borderRadius: "10px",
    marginBottom: "20px",
    fontSize: "15px",
    border: "2px solid rgba(255, 107, 107, 0.5)",
    animation: "shake 0.5s",
  },
  successMessage: {
    color: "#00ff7f",
    backgroundColor: "rgba(0, 255, 127, 0.15)",
    padding: "15px",
    borderRadius: "10px",
    marginBottom: "20px",
    fontSize: "15px",
    border: "2px solid rgba(0, 255, 127, 0.5)",
  },
  adminNote: {
    marginTop: "20px",
    padding: "15px",
    background: "rgba(0,255,127,0.1)",
    border: "1px solid rgba(0,255,127,0.3)",
    borderRadius: "8px",
    fontSize: "13px",
    color: "#aaa",
    textAlign: "left",
  },
  usersList: {
    marginTop: "15px",
    padding: "10px",
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    borderRadius: "5px",
    maxHeight: "200px",
    overflowY: "auto",
  },
  userItem: {
    padding: "5px 0",
    borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
    fontSize: "12px",
  },
};

export default LoginPage;
