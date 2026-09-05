import { useAuthStore } from "@/store/auth-store";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LoginPayload, RegisterPayload, AuthResponse } from "@/types/auth";

export function useAuth() {
  const router = useRouter();
  const { user, accessToken, isAuthenticated, setAuth, logout, updateUser } = useAuthStore();

  const login = async (payload: LoginPayload) => {
    const res = await api.post<AuthResponse>("/auth/login", payload);
    const access = res.data.access_token || res.data.tokens?.access_token || "";
    const refresh = res.data.refresh_token || res.data.tokens?.refresh_token || "";
    setAuth(res.data.user, access, refresh);
    return res.data;
  };

  const register = async (payload: RegisterPayload) => {
    const res = await api.post<AuthResponse>("/auth/register", payload);
    const access = res.data.access_token || res.data.tokens?.access_token || "";
    const refresh = res.data.refresh_token || res.data.tokens?.refresh_token || "";
    setAuth(res.data.user, access, refresh);
    return res.data;
  };

  const verifyOtp = async (email: string, otp: string) => {
    const res = await api.post<any>("/auth/verify-otp", { email, otp_code: otp });
    return res.data;
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return {
    user,
    accessToken,
    isAuthenticated,
    isInstructor: user?.role === "instructor" || user?.role === "admin",
    isAdmin: user?.role === "admin",
    login,
    register,
    verifyOtp,
    logout: handleLogout,
    updateUser,
  };
}
