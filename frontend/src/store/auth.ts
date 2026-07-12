import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Permission {
  name: string;
  description?: string;
}

export interface Role {
  name: string;
  description?: string;
  permissions: Permission[];
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  roles: Role[];
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  getPermissions: () => string[];
  hasPermission: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),
      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
      getPermissions: () => {
        const user = get().user;
        if (!user) return [];
        const perms = new Set<string>();
        user.roles.forEach((role) => {
          role.permissions.forEach((perm) => perms.add(perm.name));
        });
        return Array.from(perms);
      },
      hasPermission: (permission) => {
        return get().getPermissions().includes(permission);
      },
    }),
    {
      name: "auth-storage",
    }
  )
);
