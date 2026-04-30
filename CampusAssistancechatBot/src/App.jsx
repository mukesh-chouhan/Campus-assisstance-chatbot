import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./page/userlogin.jsx";
import ForgotPassword from "./page/ForgotPassword.jsx";
import UserDashboard from "./page/userPage.jsx";
import AdminDashboard from "./page/AdminDashboard.jsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/user" element={<UserDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
