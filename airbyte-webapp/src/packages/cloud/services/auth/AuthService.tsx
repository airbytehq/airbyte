import React, { useContext, useEffect, useState } from "react";

type Context = {
  user: User | null;
  inited: boolean;
  isLoading: boolean;
  login: (
    name: string,
    password: string,
    callBack?: () => Promise<void>
  ) => Promise<Either<SignInError, User>>;
  updateUser: (user: Partial<User>) => void;
  updateUserPassword: (
    currentPassword: string,
    newPassword: string
  ) => Promise<Either<ChangePasswordError, string>>;
  logout: () => void;
  completeNewPassword: (
    user: User,
    values: { password: string; firstName: string; lastName: string }
  ) => Promise<Either<SignUpError, User>>;
};

const defaultState: Context = {
  user: null,
  inited: false,
  isLoading: false,
  login: () => undefined,
  updateUser: () => undefined,
  updateUserPassword: () => undefined,
  logout: async () => ({}),
  completeNewPassword: async () => undefined,
};

export const AuthContext = React.createContext<Context>(defaultState);

export const useAuth = () => useContext(AuthContext);

export const AuthenticationProvider: React.FC = ({ children }) => {
  const [currentUser, updateCurrentUser] = useState<User | null>(null);
  const [inited, setInited] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const resetCache = useResetter();

  useEffect(() => {
    authService
      .getCurrentUser()
      .then((user) => {
        updateCurrentUser(user);
        return authService.getCurrentSession();
      })
      .catch(() => {})
      .finally(() => {
        setInited(true);
      });
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        inited,
        isLoading,
        login: async (
          name: string,
          password: string,
          callBack?: () => Promise<void>
        ) => {
          const result = await authService.login(name, password);

          if (isRight(result)) {
            setIsLoading(true);
            if (!result.right.segment_alias) {
              AnalyticsService.alias(result.right.id);
              await authService.updateUserAttributes({
                segment_alias: true,
              });
            }
            if (callBack) {
              await callBack();
            }
            updateCurrentUser({ ...currentUser, ...result.right });
            AnalyticsService.track("Signed In", { user_id: result.right.id });
          }

          setIsLoading(false);
          return result;
        },
        completeNewPassword: async (
          user: User,
          values: { password: string; firstName: string; lastName: string }
        ) => {
          const result = await authService.completeNewPassword(user, values);
          if (isRight(result)) {
            updateCurrentUser({ ...currentUser, ...result.right });
          }

          return result;
        },
        updateUser: async (user: Partial<User>) => {
          const result = await authService.updateUserAttributes(user);

          if (isRight(result)) {
            updateCurrentUser({ ...currentUser, ...result.right });
          }

          return result;
        },
        updateUserPassword: async (
          currentPassword: string,
          newPassword: string
        ) => {
          return await authService.updateUserPassword(
            currentPassword,
            newPassword
          );
        },
        logout: async () => {
          await authService.signOut();
          AnalyticsService.track("Signed Out", { user_id: currentUser.id });
          AnalyticsService.reset();
          updateCurrentUser(null);
          resetCache();
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
