import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

const BACKEND_URL = "http://localhost:5000";

function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    user_id: "",
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    roll_number: "",
    department: "",
    year: "",
    phone: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    // Validation
    if (!formData.email.endsWith('@iare.ac.in')) {
      setErrorMessage("Please use your IARE college email (@iare.ac.in)");
      return;
    }

    if (formData.password.length < 6) {
      setErrorMessage("Password must be at least 6 characters");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setErrorMessage("Passwords do not match");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: formData.user_id,
          email: formData.email,
          password: formData.password,
          name: formData.name,
          roll_number: formData.roll_number,
          department: formData.department,
          year: parseInt(formData.year) || null,
          phone: formData.phone
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMessage(data.error || "Registration failed");
        setIsLoading(false);
        return;
      }

      if (data.success) {
        setSuccessMessage("Registration successful! Redirecting to login...");
        setTimeout(() => {
          navigate("/");
        }, 2000);
      }
    } catch (err) {
      console.error("Registration error:", err);
      setErrorMessage("Registration failed. Please try again.");
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
            overflow-x: hidden;
          }
        `}
      </style>
      <div style={styles.container}>
        <form style={styles.form} onSubmit={handleRegister}>
          <div style={styles.logoContainer}>
            <div style={styles.logo}>📝</div>
            <h2 style={styles.title}>Student Registration</h2>
            <p style={styles.tagline}>IARE Campus Assistant</p>
          </div>

          <input
            type="text"
            name="user_id"
            placeholder="User ID (e.g., student_123) *"
            style={styles.input}
            value={formData.user_id}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="name"
            placeholder="Full Name *"
            style={styles.input}
            value={formData.name}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="College Email (e.g., student@iare.ac.in) *"
            style={styles.input}
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="roll_number"
            placeholder="Roll Number (e.g., R210001)"
            style={styles.input}
            value={formData.roll_number}
            onChange={handleChange}
          />

          <select
            name="department"
            style={styles.input}
            value={formData.department}
            onChange={handleChange}
          >
            <option value="">Select Department</option>
            <option value="CSE">Computer Science Engineering</option>
            <option value="CSE-AIML">CSE - AI & ML</option>
            <option value="CSE-DS">CSE - Data Science</option>
            <option value="ECE">Electronics & Communication</option>
            <option value="EEE">Electrical & Electronics</option>
            <option value="MECH">Mechanical Engineering</option>
            <option value="CIVIL">Civil Engineering</option>
            <option value="IT">Information Technology</option>
          </select>

          <select
            name="year"
            style={styles.input}
            value={formData.year}
            onChange={handleChange}
          >
            <option value="">Select Year</option>
            <option value="1">1st Year</option>
            <option value="2">2nd Year</option>
            <option value="3">3rd Year</option>
            <option value="4">4th Year</option>
          </select>

          <input
            type="tel"
            name="phone"
            placeholder="Phone Number"
            style={styles.input}
            value={formData.phone}
            onChange={handleChange}
          />

          <div style={styles.passwordWrapper}>
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Password (min 6 characters) *"
              style={styles.input}
              value={formData.password}
              onChange={handleChange}
              required
            />
            <span
              onClick={() => setShowPassword(!showPassword)}
              style={styles.eyeIcon}
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          <input
            type={showPassword ? "text" : "password"}
            name="confirmPassword"
            placeholder="Confirm Password *"
            style={styles.input}
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />

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
            {isLoading ? "Registering..." : "Register"}
          </button>

          <div style={styles.linkText}>
            Already have an account? <Link to="/" style={styles.link}>Login here</Link>
          </div>
        </form>
      </div>
    </>
  );
}

const styles = {
  container: {
    display: "flex",
    minHeight: "100vh",
    width: "100vw",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #000 0%, #0a3d0a 50%, #00ff7f 100%)",
    padding: "20px 0",
  },
  form: {
    backgroundColor: "rgba(0,0,0,0.9)",
    padding: "40px",
    borderRadius: "20px",
    boxShadow: "0px 0px 40px rgba(0,255,127,0.4)",
    border: "2px solid rgba(0,255,127,0.3)",
    width: "450px",
    maxWidth: "90%",
    textAlign: "center",
    backdropFilter: "blur(10px)",
    marginTop: "20px",
    marginBottom: "20px",
  },
  logoContainer: {
    marginBottom: "25px",
  },
  logo: {
    fontSize: "3.5rem",
    marginBottom: "10px",
    filter: "drop-shadow(0 0 10px #00ff7f)",
  },
  title: {
    color: "#00ff7f",
    marginBottom: "5px",
    fontSize: "26px",
    fontWeight: "bold",
    textShadow: "0 0 20px rgba(0,255,127,0.5)",
  },
  tagline: {
    color: "#888",
    fontSize: "14px",
    marginTop: "5px",
  },
  input: {
    width: "100%",
    padding: "14px",
    marginBottom: "16px",
    borderRadius: "10px",
    border: "2px solid rgba(0,255,127,0.3)",
    outline: "none",
    fontSize: "15px",
    backgroundColor: "rgba(0,255,127,0.05)",
    color: "white",
    transition: "all 0.3s ease",
  },
  button: {
    width: "100%",
    padding: "15px",
    background: "linear-gradient(135deg, #00ff7f 0%, #00cc66 100%)",
    color: "#000",
    fontWeight: "bold",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "17px",
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
    marginTop: "-8px",
  },
  linkText: {
    marginTop: "20px",
    color: "white",
    fontSize: "15px",
  },
  link: {
    color: "#00ff7f",
    textDecoration: "none",
    fontWeight: "bold",
  },
  errorMessage: {
    color: "#ff6b6b",
    backgroundColor: "rgba(255, 107, 107, 0.15)",
    padding: "12px",
    borderRadius: "10px",
    marginBottom: "15px",
    fontSize: "14px",
    border: "2px solid rgba(255, 107, 107, 0.5)",
  },
  successMessage: {
    color: "#00ff7f",
    backgroundColor: "rgba(0, 255, 127, 0.15)",
    padding: "12px",
    borderRadius: "10px",
    marginBottom: "15px",
    fontSize: "14px",
    border: "2px solid rgba(0, 255, 127, 0.5)",
  },
};

export default RegisterPage;
