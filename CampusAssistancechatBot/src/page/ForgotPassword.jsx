import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FaEye, FaEyeSlash, FaKey, FaLock } from "react-icons/fa";

const BACKEND_URL = "http://localhost:5000";

function ForgotPassword() {
  const [step, setStep] = useState(1); 
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    securityAnswer: "",
    newPassword: "",
    confirmPassword: ""
  });
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!formData.email) {
      setErrorMessage("Please enter your email");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.email }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMessage(data.error || "Email not found");
        setIsLoading(false);
        return;
      }

      if (data.success) {
        setSecurityQuestion(data.security_question);
        setStep(2);
      }
    } catch (err) {
      console.error("Error:", err);
      setErrorMessage("Failed to process request. Server might be offline.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSecurityAnswer = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!formData.securityAnswer) {
      setErrorMessage("Please answer the security question");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/verify-answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email: formData.email,
          answer: formData.securityAnswer 
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMessage(data.error || "Incorrect answer");
        setIsLoading(false);
        return;
      }

      if (data.success) {
        setStep(3);
      }
    } catch (err) {
      console.error("Error:", err);
      setErrorMessage("Failed to verify answer");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!formData.newPassword || !formData.confirmPassword) {
      setErrorMessage("Please fill all fields");
      return;
    }

    if (formData.newPassword.length < 6) {
      setErrorMessage("Password must be at least 6 characters");
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setErrorMessage("Passwords do not match");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email: formData.email,
          new_password: formData.newPassword 
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMessage(data.error || "Failed to reset password");
        setIsLoading(false);
        return;
      }

      if (data.success) {
        setSuccessMessage("Password reset successful! Redirecting to login...");
        setTimeout(() => {
          navigate("/");
        }, 2000);
      }
    } catch (err) {
      console.error("Error:", err);
      setErrorMessage("Failed to reset password");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
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
        <form style={styles.form} onSubmit={
          step === 1 ? handleEmailSubmit : 
          step === 2 ? handleSecurityAnswer : 
          handlePasswordReset
        }>
          <div style={styles.logoContainer}>
            <div style={styles.logo}><FaKey /></div>
            <h2 style={styles.title}>Forgot Password</h2>
            <p style={styles.tagline}>
              {step === 1 && "Enter your email to reset password"}
              {step === 2 && "Answer security question"}
              {step === 3 && "Create new password"}
            </p>
          </div>

          <div style={styles.progressBar}>
            <div style={{...styles.progressStep, ...(step >= 1 ? styles.progressStepActive : {})}}>1</div>
            <div style={{...styles.progressLine, ...(step >= 2 ? styles.progressLineActive : {})}} />
            <div style={{...styles.progressStep, ...(step >= 2 ? styles.progressStepActive : {})}}>2</div>
            <div style={{...styles.progressLine, ...(step >= 3 ? styles.progressLineActive : {})}} />
            <div style={{...styles.progressStep, ...(step >= 3 ? styles.progressStepActive : {})}}>3</div>
          </div>

          {step === 1 && (
            <>
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                style={styles.input}
                value={formData.email}
                onChange={handleChange}
                required
              />
            </>
          )}

          {step === 2 && (
            <>
              <div style={styles.questionBox}>
                <strong>{securityQuestion}</strong>
              </div>
              <input
                type="text"
                name="securityAnswer"
                placeholder="Your answer"
                style={styles.input}
                value={formData.securityAnswer}
                onChange={handleChange}
                required
              />
            </>
          )}

          {step === 3 && (
            <>
              <div style={styles.passwordWrapper}>
                <input
                  type={showPassword ? "text" : "password"}
                  name="newPassword"
                  placeholder="New Password (min 6 characters)"
                  style={styles.input}
                  value={formData.newPassword}
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
                placeholder="Confirm New Password"
                style={styles.input}
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </>
          )}

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
            {isLoading ? "Processing..." : 
              step === 1 ? "Continue" : 
              step === 2 ? "Verify Answer" : 
              "Reset Password"
            }
          </button>

          <div style={styles.linkText}>
            Remember your password? <Link to="/" style={styles.link}>Login here</Link>
          </div>
        </form>
      </div>
    </>
  );
}

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
  },
  logoContainer: {
    marginBottom: "30px",
  },
  logo: {
    fontSize: "3.5rem",
    marginBottom: "10px",
    color: "#00ff7f",
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
  progressBar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "30px",
    gap: "0px",
  },
  progressStep: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    background: "rgba(100, 116, 139, 0.3)",
    border: "2px solid #64748b",
    color: "#64748b",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "bold",
    fontSize: "16px",
    transition: "all 0.3s ease",
  },
  progressStepActive: {
    background: "linear-gradient(135deg, #00ff7f, #00cc66)",
    border: "2px solid #00ff7f",
    color: "#000",
    boxShadow: "0 0 15px rgba(0,255,127,0.5)",
  },
  progressLine: {
    width: "60px",
    height: "3px",
    background: "#64748b",
    transition: "all 0.3s ease",
  },
  progressLineActive: {
    background: "linear-gradient(90deg, #00ff7f, #00cc66)",
    boxShadow: "0 0 10px rgba(0,255,127,0.5)",
  },
  questionBox: {
    background: "rgba(0,255,127,0.1)",
    border: "2px solid rgba(0,255,127,0.3)",
    borderRadius: "10px",
    padding: "16px",
    marginBottom: "20px",
    color: "#00ff7f",
    fontSize: "15px",
    textAlign: "left",
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
    marginTop: "-10px",
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

export default ForgotPassword;
