import React, { createContext, useContext } from "react";
import { useNavigate } from "react-router-dom";

import useStateCallback from "hooks/useStateCallback";
import { RoutePaths } from "pages/routePaths";

import { IAuthUser, MyAuthUser } from "./authenticatedUser";

interface IUserContext {
  user: IAuthUser;
  setUser?: (user: IAuthUser) => void;
  removeUser?: () => void;
}

const AUTH_USER_KEY = "daspire-user";

export const getUser = (): IAuthUser => {
  const user: IAuthUser | null = JSON.parse(localStorage.getItem(AUTH_USER_KEY) as string);
  if (user?.token) {
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

  const removeUser = () => {
    localStorage.removeItem(AUTH_USER_KEY);
    setAuthenticatedUser(MyAuthUser.userJSON(), () => window.location.reload());
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
