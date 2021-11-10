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
import { User } from "packages/cloud/lib/domain/users";
import { AuthProviders } from "packages/cloud/lib/auth/AuthProviders";
import { useGetUserService } from "packages/cloud/services/users/UserService";
import { useAuth } from "packages/firebaseReact";

export type AuthUpdatePassword = (
  email: string,
  currentPassword: string,
  newPassword: string
) => Promise<void>;

export type AuthRequirePasswordReset = (email: string) => Promise<void>;
export type AuthConfirmPasswordReset = (
  code: string,
  newPassword: string
) => Promise<void>;

export type AuthLogin = (values: {
  email: string;
  password: string;
}) => Promise<void>;

export type AuthSignUp = (form: {
  email: string;
  password: string;
}) => Promise<User | null>;

export type AuthChangeEmail = (
  email: string,
  password: string
) => Promise<void>;

export type AuthSendEmailVerification = () => Promise<void>;
export type AuthVerifyEmail = (code: string) => Promise<void>;
export type AuthLogout = () => void;

type AuthContextApi = {
  user: User | null;
  inited: boolean;
  emailVerified: boolean;
  isLoading: boolean;
  login: AuthLogin;
  signUp: AuthSignUp;
  updatePassword: AuthUpdatePassword;
  updateEmail: AuthChangeEmail;
  requirePasswordReset: AuthRequirePasswordReset;
  confirmPasswordReset: AuthConfirmPasswordReset;
  sendEmailVerification: AuthSendEmailVerification;
  verifyEmail: AuthVerifyEmail;
  logout: AuthLogout;
};

export const AuthContext = React.createContext<AuthContextApi | null>(null);

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [
    state,
    { loggedIn, emailVerified, authInited, loggedOut },
  ] = useTypesafeReducer<AuthServiceState, typeof actions>(
    authStateReducer,
    initialState,
    actions
  );
  const auth = useAuth();
  const userService = useGetUserService();
  const authService = useMemo(() => new GoogleAuthService(() => auth), [auth]);

  useEffect(() => {
    return auth.onAuthStateChanged(async (currentUser) => {
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
      async login(values: { email: string; password: string }): Promise<void> {
        await authService.login(values.email, values.password);
      },
      async logout(): Promise<void> {
        await authService.signOut();
        loggedOut();
        await queryClient.invalidateQueries();
      },
      async updateEmail(email, password): Promise<void> {
        await userService.changeEmail(email);
        return authService.updateEmail(email, password);
      },
      async updatePassword(
        email: string,
        currentPassword: string,
        newPassword: string
      ): Promise<void> {
        // re-authentication may be needed before updating password
        // https://firebase.google.com/docs/auth/web/manage-users#re-authenticate_a_user
        await authService.reauthenticate(email, currentPassword);
        return authService.updatePassword(newPassword);
      },
      async requirePasswordReset(email: string): Promise<void> {
        await authService.resetPassword(email);
      },
      async sendEmailVerification(): Promise<void> {
        await authService.sendEmailVerifiedLink();
      },
      async verifyEmail(code: string): Promise<void> {
        await authService.confirmEmailVerify(code);
        emailVerified(true);
      },
      async confirmPasswordReset(
        code: string,
        newPassword: string
      ): Promise<void> {
        await authService.finishResetPassword(code, newPassword);
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

        await authService.sendEmailVerifiedLink();
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
