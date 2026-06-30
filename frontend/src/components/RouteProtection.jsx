import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

const RouteProtection = () => {
  const { isLoggedIn } = useAuth();

  return isLoggedIn ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace />
  );
};

export default RouteProtection;