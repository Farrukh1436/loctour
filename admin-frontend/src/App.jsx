import { Routes, Route, Navigate } from "react-router-dom";
import { Spin } from "antd";
import { AuthProvider, useAuth } from "./contexts/AuthContext.jsx";
import AppLayout from "./components/AppLayout.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import TripsPage from "./pages/TripsPage.jsx";
import TripDetailPage from "./pages/TripDetailPage.jsx";
import PlacesPage from "./pages/PlacesPage.jsx";
import TravelersPage from "./pages/TravelersPage.jsx";
import ExpensesPage from "./pages/ExpensesPage.jsx";
import SettingsPage from "./pages/SettingsPage.jsx";

function ProtectedRoutes() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh"
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/trips" element={<TripsPage />} />
        <Route path="/trips/:id" element={<TripDetailPage />} />
        <Route path="/places" element={<PlacesPage />} />
        <Route path="/travelers" element={<TravelersPage />} />
        <Route path="/expenses" element={<ExpensesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppLayout>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ProtectedRoutes />
    </AuthProvider>
  );
}
