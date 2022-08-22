import { User as FirebaseUser } from "firebase/auth";
import React, { useCallback, useContext, useMemo, useRef } from "react";
import { useQueryClient } from "react-query";
import { useEffectOnce } from "react-use";
import { Observable, Subject } from "rxjs";

import { Action, Namespace } from "core/analytics";
import { isCommonRequestError } from "core/request/CommonRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import useTypesafeReducer from "hooks/useTypesafeReducer";
import { AuthProviders, OAuthProviders } from "packages/cloud/lib/auth/AuthProviders";
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

type OAuthLoginState = "waiting" | "loading" | "done";

interface AuthContextApi {
  user: User | null;
  inited: boolean;
  emailVerified: boolean;
  isLoading: boolean;
  loggedOut: boolean;
  providers: string[] | null;
  hasPasswordLogin: () => boolean;
  login: AuthLogin;
  loginWithOAuth: (provider: OAuthProviders) => Observable<OAuthLoginState>;
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

  /**
   * Create a user object in the Airbyte database from an existing Firebase user.
   * This will make sure that the user account is tracked in our database as well
   * as create a workspace for that user. This method also takes care of sending
   * the relevant user creation analytics events.
   */
  const createAirbyteUser = async (
    firebaseUser: FirebaseUser,
    userData: { name?: string; companyName?: string; news?: boolean } = {}
  ): Promise<User> => {
    // Create the Airbyte user on our server
    const user = await userService.create({
      authProvider: AuthProviders.GoogleIdentityPlatform,
      authUserId: firebaseUser.uid,
      email: firebaseUser.email ?? "",
      name: userData.name ?? firebaseUser.displayName ?? "",
      companyName: userData.companyName ?? "",
      news: userData.news ?? false,
    });

    analytics.track(Namespace.USER, Action.CREATE, {
      actionDescription: "New user registered",
      user_id: firebaseUser.uid,
      name: user.name,
      email: user.email,
      // Which login provider was used, e.g. "password", "google.com", "github.com"
      provider: firebaseUser.providerData[0]?.providerId,
      ...getUtmFromStorage(),
    });

    return user;
  };

  const onAfterAuth = useCallback(
    async (currentUser: FirebaseUser, user?: User) => {
      try {
        user ??= await userService.getByAuthId(currentUser.uid, AuthProviders.GoogleIdentityPlatform);
        loggedIn({
          user,
          emailVerified: currentUser.emailVerified,
          providers: currentUser.providerData.map(({ providerId }) => providerId),
        });
      } catch (e) {
        if (isCommonRequestError(e) && e.status === 404) {
          // If there is a firebase user but not database user we'll create a db user in this step
          // and retry the onAfterAuth step. This will always happen when a user logins via OAuth
          // the first time and we don't have a database user yet for them. In rare cases this can
          // also happen for email/password users if they closed their browser or got some network
          // errors in between creating the firebase user and the database user originally.
          const user = await createAirbyteUser(currentUser);
          await onAfterAuth(currentUser, user);
        } else {
          throw e;
        }
      }
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
      providers: state.providers,
      hasPasswordLogin(): boolean {
        return !!state.providers?.includes("password");
      },
      async login(values: { email: string; password: string }): Promise<void> {
        await authService.login(values.email, values.password);

        if (auth.currentUser) {
          await onAfterAuth(auth.currentUser);
        }
      },
      loginWithOAuth(provider): Observable<OAuthLoginState> {
        const state = new Subject<OAuthLoginState>();
        try {
          state.next("waiting");
          authService
            .loginWithOAuth(provider)
            .then(async () => {
              state.next("loading");
              if (auth.currentUser) {
                await onAfterAuth(auth.currentUser);
                state.next("done");
                state.complete();
              }
            })
            .catch((e) => state.error(e));
        } catch (e) {
          state.error(e);
        }
        return state.asObservable();
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
        let firebaseUser: FirebaseUser;

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
        const { user: firebaseUser } = await authService.signUp(form.email, form.password);

        // Create a user in our database for that firebase user
        await createAirbyteUser(firebaseUser, { name: form.name, companyName: form.companyName, news: form.news });

        // Send verification mail via firebase
        await authService.sendEmailVerifiedLink();

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
