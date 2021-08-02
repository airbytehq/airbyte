import React, { useContext, useEffect, useMemo } from "react";

import { User } from "./types";
import { GoogleAuthService } from "./GoogleAuthService";
import useTypesafeReducer from "components/hooks/useTypesafeReducer";
import {
  actions,
  AuthServiceState,
  authStateReducer,
  initialState,
} from "./reducer";
import { firebaseApp } from "packages/cloud/config/firebase";

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

const authService = new GoogleAuthService();

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [state, { loggedIn, authInited }] = useTypesafeReducer<
    AuthServiceState,
    typeof actions
  >(authStateReducer, initialState, actions);

  useEffect(() => {
    firebaseApp.auth().onAuthStateChanged(async (currentUser) => {
      if (state.currentUser === null && currentUser) {
        const token = await currentUser.getIdToken();

        // TODO: place token into right place
        loggedIn({
          token,
        });
      } else {
        authInited();
      }
    });
  }, [state.currentUser, loggedIn, authInited]);

  const ctx: Context = useMemo(
    () => ({
      inited: state.inited,
      isLoading: state.loading,
      async login(values: {
        email: string;
        password: string;
      }): Promise<User | null> {
        const user = await authService.login(values.email, values.password);
        return user;
      },
      async logout(): Promise<void> {
        await authService.signOut();
      },
      async signUp(form: {
        email: string;
        password: string;
      }): Promise<User | null> {
        const user = await authService.signUp(form.email, form.password);
        await Promise.resolve(() => console.log("add extra fields"));

        return user;
      },
      user: state.currentUser,
    }),
    [state]
  );

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
