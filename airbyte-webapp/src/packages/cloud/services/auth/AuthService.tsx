import React, { useContext, useEffect, useMemo } from "react";
import { useQueryClient } from "react-query";

import { GoogleAuthService } from "packages/cloud/lib/auth/GoogleAuthService";
import useTypesafeReducer from "hooks/useTypesafeReducer";
import {
  actions,
  AuthServiceState,
  authStateReducer,
  initialState,
} from "./reducer";
import { firebaseApp } from "packages/cloud/config/firebase";
import { User } from "packages/cloud/lib/domain/users";
import { AuthProviders } from "packages/cloud/lib/auth/AuthProviders";
import { useGetUserService } from "packages/cloud/services/users/UserService";

type AuthContextApi = {
  user: User | null;
  inited: boolean;
  emailVerified: boolean;
  isLoading: boolean;
  login: (values: { email: string; password: string }) => Promise<User | null>;
  signUp: (form: { email: string; password: string }) => Promise<User | null>;
  requirePasswordReset: (email: string) => Promise<void>;
  confirmPasswordReset: (code: string, newPassword: string) => Promise<void>;
  sendEmailVerification: () => Promise<void>;
  verifyEmail: (code: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = React.createContext<AuthContextApi | null>(null);

// TODO: add proper DI service
const authService = new GoogleAuthService();

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [
    state,
    { loggedIn, emailVerified, authInited, loggedOut },
  ] = useTypesafeReducer<AuthServiceState, typeof actions>(
    authStateReducer,
    initialState,
    actions
  );
  const userService = useGetUserService();

  useEffect(() => {
    firebaseApp.auth().onAuthStateChanged(async (currentUser) => {
      if (state.currentUser === null && currentUser) {
        // token = await currentUser.getIdToken();

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
          loggedIn({ user, emailVerified: currentUser.emailVerified });
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
      emailVerified: state.emailVerified,
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
      async requirePasswordReset(email: string): Promise<void> {
        await authService.resetPassword(email);
      },
      async sendEmailVerification(): Promise<void> {
        await authService.getCurrentUser()?.sendEmailVerification();
      },
      async verifyEmail(code: string): Promise<void> {
        await firebaseApp.auth().applyActionCode(code);
        emailVerified(true);
      },
      async confirmPasswordReset(code: string, email: string): Promise<void> {
        await firebaseApp.auth().confirmPasswordReset(code, email);
      },
      async signUp(form: {
        email: string;
        password: string;
      }): Promise<User | null> {
        const user = await authService.signUp(form.email, form.password);
        // const user = await userService.create({
        //   authProvider: AuthProviders.GoogleIdentityPlatform,
        //   authUserId: fbUser.user!.uid,
        //   email: form.email,
        //   name: form.email,
        // });

        await user.sendEmailVerification();
        return null;
      },
      user: state.currentUser,
    }),
    [state, queryClient, userService]
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
