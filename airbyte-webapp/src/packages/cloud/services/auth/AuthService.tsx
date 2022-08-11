import { User as FbUser } from "firebase/auth";
import React, { useCallback, useContext, useMemo, useRef } from "react";
import { useQueryClient } from "react-query";
import { useEffectOnce } from "react-use";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import useTypesafeReducer from "hooks/useTypesafeReducer";
import { AuthProviders } from "packages/cloud/lib/auth/AuthProviders";
import { GoogleAuthService } from "packages/cloud/lib/auth/GoogleAuthService";
import { User } from "packages/cloud/lib/domain/users";
import { useGetUserService } from "packages/cloud/services/users/UserService";
import { useAuth } from "packages/firebaseReact";
import { useInitService } from "services/useInitService";
import { getUtmFromStorage } from "utils/utmStorage";

import { actions, AuthServiceState, authStateReducer, initialState } from "./reducer";
import { EmailLinkErrorCodes } from "./types";

export type AuthUpdatePassword = (email: string, currentPassword: string, newPassword: string) => Promise<void>;

export type AuthRequirePasswordReset = (email: string) => Promise<void>;
export type AuthConfirmPasswordReset = (code: string, newPassword: string) => Promise<void>;

export type AuthLogin = (values: { email: string; password: string }) => Promise<void>;

export type AuthSignUp = (form: {
  email: string;
  password: string;
  companyName: string;
  name: string;
  news: boolean;
}) => Promise<void>;

export type AuthChangeEmail = (email: string, password: string) => Promise<void>;
export type AuthChangeName = (name: string) => Promise<void>;

export type AuthSendEmailVerification = () => Promise<void>;
export type AuthVerifyEmail = (code: string) => Promise<void>;
export type AuthLogout = () => Promise<void>;

interface AuthContextApi {
  user: User | null;
  inited: boolean;
  emailVerified: boolean;
  isLoading: boolean;
  loggedOut: boolean;
  login: AuthLogin;
  signUpWithEmailLink: (form: { name: string; email: string; password: string; news: boolean }) => Promise<void>;
  signUp: AuthSignUp;
  updatePassword: AuthUpdatePassword;
  updateEmail: AuthChangeEmail;
  updateName: AuthChangeName;
  requirePasswordReset: AuthRequirePasswordReset;
  confirmPasswordReset: AuthConfirmPasswordReset;
  sendEmailVerification: AuthSendEmailVerification;
  verifyEmail: AuthVerifyEmail;
  logout: AuthLogout;
}

export const AuthContext = React.createContext<AuthContextApi | null>(null);

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [state, { loggedIn, emailVerified, authInited, loggedOut, updateUserName }] = useTypesafeReducer<
    AuthServiceState,
    typeof actions
  >(authStateReducer, initialState, actions);
  const auth = useAuth();
  const userService = useGetUserService();
  const analytics = useAnalyticsService();
  const authService = useInitService(() => new GoogleAuthService(() => auth), [auth]);

  const onAfterAuth = useCallback(
    async (currentUser: FbUser, user?: User) => {
      user ??= await userService.getByAuthId(currentUser.uid, AuthProviders.GoogleIdentityPlatform);
      loggedIn({ user, emailVerified: currentUser.emailVerified });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [userService]
  );

  const stateRef = useRef(state);
  stateRef.current = state;

  useEffectOnce(() => {
    return auth.onAuthStateChanged(async (currentUser) => {
      // We want to run this effect only once on initial page opening
      if (!stateRef.current.inited) {
        if (stateRef.current.currentUser === null && currentUser) {
          await onAfterAuth(currentUser);
        } else {
          authInited();
        }
      }
    });
  });

  const queryClient = useQueryClient();

  const ctx: AuthContextApi = useMemo(
    () => ({
      inited: state.inited,
      isLoading: state.loading,
      emailVerified: state.emailVerified,
      loggedOut: state.loggedOut,
      async login(values: { email: string; password: string }): Promise<void> {
        await authService.login(values.email, values.password);

        if (auth.currentUser) {
          await onAfterAuth(auth.currentUser);
        }
      },
      async logout(): Promise<void> {
        await userService.revokeUserSession();
        await authService.signOut();
        queryClient.removeQueries();
        loggedOut();
      },
      async updateName(name: string): Promise<void> {
        if (!state.currentUser) {
          return;
        }
        await userService.changeName(state.currentUser.authUserId, state.currentUser.userId, name);
        await authService.updateProfile(name);
        updateUserName({ value: name });
      },
      async updateEmail(email, password): Promise<void> {
        await userService.changeEmail(email);
        return authService.updateEmail(email, password);
      },
      async updatePassword(email: string, currentPassword: string, newPassword: string): Promise<void> {
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
      async confirmPasswordReset(code: string, newPassword: string): Promise<void> {
        await authService.finishResetPassword(code, newPassword);
      },
      async signUpWithEmailLink({ name, email, password, news }): Promise<void> {
        let firebaseUser: FbUser;

        try {
          ({ user: firebaseUser } = await authService.signInWithEmailLink(email));
          await authService.updatePassword(password);
        } catch (e) {
          await authService.signOut();
          if (e.message === EmailLinkErrorCodes.LINK_EXPIRED) {
            await userService.resendWithSignInLink({ email });
          }
          throw e;
        }

        if (firebaseUser) {
          const user = await userService.getByAuthId(firebaseUser.uid, AuthProviders.GoogleIdentityPlatform);
          await userService.update({ userId: user.userId, authUserId: firebaseUser.uid, name, news });
          await onAfterAuth(firebaseUser, { ...user, name });
        }
      },
      async signUp(form: {
        email: string;
        password: string;
        companyName: string;
        name: string;
        news: boolean;
      }): Promise<void> {
        // Create a user account in firebase
        const { user: fbUser } = await authService.signUp(form.email, form.password);

        // Create the Airbyte user on our server
        const user = await userService.create({
          authProvider: AuthProviders.GoogleIdentityPlatform,
          authUserId: fbUser.uid,
          email: form.email,
          name: form.name,
          companyName: form.companyName,
          news: form.news,
        });

        // Send verification mail via firebase
        await authService.sendEmailVerifiedLink();

        analytics.track(Namespace.USER, Action.CREATE, {
          actionDescription: "New user registered",
          user_id: fbUser.uid,
          name: user.name,
          email: user.email,
          ...getUtmFromStorage(),
        });

        if (auth.currentUser) {
          await onAfterAuth(auth.currentUser);
        }
      },
      user: state.currentUser,
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [state, userService]
  );

  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>;
};

export const useAuthService = (): AuthContextApi => {
  const authService = useContext(AuthContext);
  if (!authService) {
    throw new Error("useAuthService must be used within a AuthenticationService.");
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
