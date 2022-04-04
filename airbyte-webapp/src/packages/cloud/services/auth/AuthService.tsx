import React, { useCallback, useContext, useMemo, useRef } from "react";
import { useQueryClient } from "react-query";
import { User as FbUser } from "firebase/auth";
import { useEffectOnce } from "react-use";

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
import { useAnalyticsService } from "hooks/services/Analytics";
import { getUtmFromStorage } from "utils/utmStorage";
import { useInitService } from "services/useInitService";

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
  companyName: string;
  name: string;
  news: boolean;
}) => Promise<void>;

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

const getTempSignUpStorageKey = (currentUser: FbUser): string =>
  `${currentUser.uid}/temp-signup-data`;

const TempSignUpValuesProvider = {
  get: (
    currentUser: FbUser
  ): {
    companyName: string;
    name: string;
    news: boolean;
  } => {
    try {
      const key = getTempSignUpStorageKey(currentUser);

      const storedValue = localStorage.getItem(key);

      if (storedValue) {
        return JSON.parse(storedValue);
      }
    } catch (err) {
      // passthrough and return default values
    }

    return {
      companyName: "",
      name: currentUser.email ?? "",
      news: false,
    };
  },
  save: (
    currentUser: FbUser,
    v: { companyName: string; name: string; news: boolean }
  ) => {
    localStorage.setItem(
      getTempSignUpStorageKey(currentUser),
      JSON.stringify(v)
    );
  },
};

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
  const analytics = useAnalyticsService();
  const authService = useInitService(() => new GoogleAuthService(() => auth), [
    auth,
  ]);

  const onAfterAuth = useCallback(
    async (currentUser: FbUser) => {
      let user: User | undefined;

      try {
        user = await userService.getByAuthId(
          currentUser.uid,
          AuthProviders.GoogleIdentityPlatform
        );
      } catch (err) {
        if (currentUser.email) {
          const encodedData = TempSignUpValuesProvider.get(currentUser);
          user = await userService.create({
            authProvider: AuthProviders.GoogleIdentityPlatform,
            authUserId: currentUser.uid,
            email: currentUser.email,
            name: encodedData.name,
            companyName: encodedData.companyName,
            news: encodedData.news,
          });
          analytics.track("Airbyte.UI.User.Created", {
            user_id: user.userId,
            name: user.name,
            email: user.email,
            ...getUtmFromStorage(),
          });
        }
      }

      if (user) {
        loggedIn({ user, emailVerified: currentUser.emailVerified });
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
      async login(values: { email: string; password: string }): Promise<void> {
        await authService.login(values.email, values.password);

        if (auth.currentUser) {
          await onAfterAuth(auth.currentUser);
        }
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
        companyName: string;
        name: string;
        news: boolean;
      }): Promise<void> {
        const creds = await authService.signUp(form.email, form.password);
        TempSignUpValuesProvider.save(creds.user, {
          companyName: form.companyName,
          name: form.name,
          news: form.news,
        });

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
