import React, { useContext } from "react";
import firebase from "firebase";

import { User } from "./types";
import { GoogleAuthService } from "./GoogleAuthService";

type Context = {
  user: User | null;
  inited: boolean;
  isLoading: boolean;
  login: (values: { email: string; password: string }) => Promise<User | null>;
  signUp: (form: { email: string; password: string }) => Promise<User | null>;
  logout: () => void;
};

const defaultState: Context = {
  user: null,
  inited: false,
  isLoading: false,
  login: async () => null,
  signUp: async () => null,
  logout: async () => ({}),
};

export const AuthContext = React.createContext<Context>(defaultState);

export const AuthenticationProvider: React.FC = ({ children }) => {
  const authService = new GoogleAuthService();

  firebase
    .app()
    .auth()
    .onAuthStateChanged((a) => console.log(a));

  const ctx: Context = {
    inited: false,
    isLoading: false,
    async login(values: {
      email: string;
      password: string;
    }): Promise<User | null> {
      const user = await authService.login(values.email, values.password);

      console.log(user);
      return user;
    },
    logout(): void {
      // authService;
    },
    async signUp(form: {
      email: string;
      password: string;
    }): Promise<User | null> {
      const user = await authService.signUp(form.email, form.password);
      await Promise.resolve(() => console.log("add extra fields"));

      return user;
    },
    user: null,
  };
  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>;
};

export const useAuthService = (): Context => {
  const authService = useContext(AuthContext);
  if (!authService) {
    throw new Error(
      "useAuthService must be used within a AuthenticationService."
    );
  }

  return authService;
};
