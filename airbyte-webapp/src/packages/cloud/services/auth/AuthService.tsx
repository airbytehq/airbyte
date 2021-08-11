import React, { useContext, useEffect, useMemo } from "react";
import { useQueryClient } from "react-query";

import { GoogleAuthService } from "packages/cloud/lib/auth/GoogleAuthService";
import useTypesafeReducer from "components/hooks/useTypesafeReducer";
import {
  actions,
  AuthServiceState,
  authStateReducer,
  initialState,
} from "./reducer";
import { firebaseApp } from "packages/cloud/config/firebase";
import { User, UserService } from "packages/cloud/lib/domain/users";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { AuthProviders } from "packages/cloud/lib/auth/AuthProviders";
import { api } from "packages/cloud/config/api";

type AuthContextApi = {
  user: User | null;
  inited: boolean;
  isLoading: boolean;
  login: (values: { email: string; password: string }) => Promise<User | null>;
  signUp: (form: { email: string; password: string }) => Promise<User | null>;
  resetPassword: (email: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = React.createContext<AuthContextApi | null>(null);

// TODO: place token into right place
export let token = "";

// TODO: add proper DI service
const authService = new GoogleAuthService();
const userService = new UserService(
  [
    RequestAuthMiddleware({
      getValue(): string {
        return token;
      },
    }),
  ],
  api.cloud
);

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [state, { loggedIn, authInited, loggedOut }] = useTypesafeReducer<
    AuthServiceState,
    typeof actions
  >(authStateReducer, initialState, actions);

  useEffect(() => {
    firebaseApp.auth().onAuthStateChanged(async (currentUser) => {
      if (state.currentUser === null && currentUser) {
        token = await currentUser.getIdToken();

        let user: User | undefined;

        try {
          user = await userService.getByAuthId(
            currentUser.uid,
            AuthProviders.GoogleIdentityPlatform
          );
        } catch (err) {
          if (currentUser.email) {
            user = await userService.create({
              authProvider: AuthProviders.GoogleIdentityPlatform,
              authUserId: currentUser.uid,
              email: currentUser.email,
              name: currentUser.email,
            });
          }
        }

        if (user) {
          loggedIn(user);
        }
      } else {
        authInited();
      }
    });
  }, [state.currentUser, loggedIn, authInited]);

  const queryClient = useQueryClient();

  const ctx: AuthContextApi = useMemo(
    () => ({
      inited: state.inited,
      isLoading: state.loading,
      async login(values: {
        email: string;
        password: string;
      }): Promise<User | null> {
        await authService.login(values.email, values.password);

        return null;
      },
      async logout(): Promise<void> {
        await authService.signOut();
        loggedOut();
        await queryClient.invalidateQueries();
      },
      async resetPassword(email: string): Promise<void> {
        await authService.resetPassword(email);
      },
      async confirmPasswordReset(_email: string, _code: string): Promise<void> {
        throw new Error("not yet implemented");
      },
      async signUp(form: {
        email: string;
        password: string;
      }): Promise<User | null> {
        await authService.signUp(form.email, form.password);
        // const user = await userService.create({
        //   authProvider: AuthProviders.GoogleIdentityPlatform,
        //   authUserId: fbUser.user!.uid,
        //   email: form.email,
        //   name: form.email,
        // });

        return null;
      },
      user: state.currentUser,
    }),
    [state, queryClient]
  );

  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>;
};

export const useAuthService = (): AuthContextApi => {
  const authService = useContext(AuthContext);
  if (!authService) {
    throw new Error(
      "useAuthService must be used within a AuthenticationService."
    );
  }

  return authService;
};

export const useCurrentUser = (): User => {
  const { user } = useAuthService();
  if (!user) {
    throw new Error("useCurrentUser must be used only within authorised flow");
  }

  return user;
};
