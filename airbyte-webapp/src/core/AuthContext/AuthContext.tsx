import React, { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";

import { RoutePaths } from "pages/routePaths";

export interface IAuthUser {
  account: string;
  company: string;
  expiresTime: number;
  firstName: string;
  lang: string;
  lastName: string;
  role: number;
  status: number;
  token: string;
  workspaceId: string;
}

interface IUserContext {
  user: IAuthUser;
  setUser?: (user: IAuthUser) => void;
  removeUser?: () => void;
}

const AUTH_USER_KEY = "daspire-user";

export const getUser = () => {
  return JSON.parse(localStorage.getItem(AUTH_USER_KEY) as string);
};

// initialize the context with an empty object
const UserContext = createContext<IUserContext>({
  user: getUser(),
});

export const AuthContextProvider: React.FC = ({ children }) => {
  const navigate = useNavigate();

  const [authenticatedUser, setAuthenticatedUser] = useState<IAuthUser>(() => {
    return getUser();
  });

  const setUser = (user: IAuthUser) => {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    setAuthenticatedUser(user);
    navigate(`/${RoutePaths.Connections}`);
  };

  const removeUser = () => {
    localStorage.removeItem(AUTH_USER_KEY);
    setAuthenticatedUser(() => {
      return getUser();
    });
    navigate(`/${RoutePaths.Signin}`);
  };

  return (
    <UserContext.Provider value={{ user: authenticatedUser, setUser, removeUser }}>{children}</UserContext.Provider>
  );
};

// export the hook so we can use it in other components.
export const useUser = () => {
  const ctx = useContext<IUserContext>(UserContext);
  return ctx;
};
