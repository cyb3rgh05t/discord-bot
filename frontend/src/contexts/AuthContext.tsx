import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import api from "@/lib/api";

interface User {
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  authEnabled: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authEnabled, setAuthEnabled] = useState(true);

  useEffect(() => {
    // Check auth status first
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if auth is enabled on the backend
      const statusResponse = await api.get("/auth/status");

      if (!statusResponse.data.auth_enabled) {
        // Auth is disabled, set a default user and dummy token
        setAuthEnabled(false);
        localStorage.setItem("token", "no-auth-required");
        setUser({ username: "guest" });
        setIsLoading(false);
        return;
      }

      setAuthEnabled(true);

      // Auth is enabled, check if user has a token
      const token = localStorage.getItem("token");
      if (token && token !== "no-auth-required") {
        await fetchUser();
      } else {
        setIsLoading(false);
      }
    } catch (error) {
      console.error("Failed to check auth status:", error);
      // Assume auth is disabled if we can't reach the server
      setAuthEnabled(false);
      localStorage.setItem("token", "no-auth-required");
      setUser({ username: "guest" });
      setIsLoading(false);
    }
  };

  const fetchUser = async () => {
    try {
      const response = await api.get("/auth/me");
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem("token");
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await api.post("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    const { access_token } = response.data;
    localStorage.setItem("token", access_token);
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, login, logout, isLoading, authEnabled }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
