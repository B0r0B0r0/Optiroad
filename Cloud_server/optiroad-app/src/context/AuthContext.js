import { createContext, useState, useEffect, useContext } from "react";
import { getCurrentUser, saveUser, removeUser } from "../services/storageService";
import { refreshAccessToken } from "../services/authService";
import { getUserProfile, loginUser } from "../services/authService";
import { logoutUser } from "../services/authService";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      try {
        console.log("Trying to refresh token...");
        const success = await refreshAccessToken();
        console.log("Access token refresh response:", success);
        if (success) {
          const profile = await getUserProfile();
          const updatedUser = { ...profile };

          setUser(updatedUser);
        }
      } catch (error) {
         console.warn("Token refresh failed:", error);
        removeUser();
        setUser(null);
      }
      setIsLoading(false);
    };

    verifyToken();
    setIsLoading(false);
  }, []);

  const login = async (credentials) => {
    await loginUser(credentials);
    const profile = await getUserProfile();  
    const fullUser = { ...profile };

    setUser(fullUser);
  };



  const logout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      removeUser();
      setUser(null);
    }
  };
  

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
