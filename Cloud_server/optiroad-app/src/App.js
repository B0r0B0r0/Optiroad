import {React} from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Homepage from "./pages/Homepage";
import CityPage from "./pages/CityPage";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./routes/ProtectedRoute";
import AccountSettings from "./pages/AccountSettings";
import { AuthProvider } from "./context/AuthContext";
import AddCity from "./pages/AddCity";
import PendingUsers from "./pages/PendingUsers";
import TrafficAnalytics from "./pages/TrafficAnalytics";

const App = () => {

  return (
      <AuthProvider>
      <Router>
        <Routes>
          <Route path="/dashboard" element={<ProtectedRoute ><Dashboard /></ProtectedRoute>} />
          <Route path="/city/:cityName" element={<ProtectedRoute><CityPage /></ProtectedRoute>} />
          <Route path="/register-city" element={<ProtectedRoute><AddCity /></ProtectedRoute>} />
          <Route path="/accSettings" element={<ProtectedRoute><AccountSettings /></ProtectedRoute>} />
          <Route path="/city/:cityName/analytics" element={<ProtectedRoute><TrafficAnalytics /></ProtectedRoute>} />
          <Route path="/pending-users" element={<ProtectedRoute><PendingUsers /></ProtectedRoute>} />
          <Route path="/*" element={<Homepage />} />
        </Routes>
      </Router>
      </AuthProvider>
  );
};

export default App;
