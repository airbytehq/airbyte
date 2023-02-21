import React, { createContext, useContext } from "react";
import { useNavigate } from "react-router-dom";

import useStateCallback from "hooks/useStateCallback";
import { RoutePaths } from "pages/routePaths";

import { IAuthUser, MyAuthUser } from "./authenticatedUser";

interface IUserContext {
  user: IAuthUser;
  setUser?: (user: IAuthUser) => void;
  updateUserStatus?: (status: number) => void;
  updateUserRole?: (role: number) => void;
  updateUserLang?: (lang: string) => void;
  removeUser?: () => void;
}

const AUTH_USER_KEY = "daspire-user";

export const getUser = (): IAuthUser => {
  const user: IAuthUser | null = JSON.parse(localStorage.getItem(AUTH_USER_KEY) as string);
  if (user?.token) {
    return user;
  }
  if (user?.lang) {
    return user;
  }
  return MyAuthUser.userJSON();
};

// initialize the context with an empty object
const UserContext = createContext<IUserContext>({ user: getUser() });

export const AuthContextProvider: React.FC = ({ children }) => {
  const navigate = useNavigate();

  const [authenticatedUser, setAuthenticatedUser] = useStateCallback<IAuthUser>(getUser());

  const setUser = (user: IAuthUser) => {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    setAuthenticatedUser(user, () => navigate(`/${RoutePaths.Connections}`));
  };

  const updateUserStatus = (status: number) => {
    const updatedUser = { ...authenticatedUser, status };
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(updatedUser));
    setAuthenticatedUser(updatedUser);
  };

  const updateUserRole = (role: number) => {
    const updatedUser = { ...authenticatedUser, role };
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(updatedUser));
    setAuthenticatedUser(updatedUser);
  };

  const updateUserLang = (lang: string) => {
    const updatedUser = { ...authenticatedUser, lang };
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(updatedUser));
    setAuthenticatedUser(updatedUser);
  };

  const removeUser = () => {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(MyAuthUser.logoutUser(authenticatedUser)));
    setAuthenticatedUser(MyAuthUser.logoutUser(authenticatedUser), () => window.location.reload());
  };

  return (
    <UserContext.Provider
      value={{
        user: authenticatedUser,
        setUser,
        updateUserStatus,
        updateUserRole,
        updateUserLang,
        removeUser,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

// export the hook so we can use it in other components.
export const useUser = () => {
  const ctx = useContext<IUserContext>(UserContext);
  return ctx;
};
