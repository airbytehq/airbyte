export interface IAuthUser {
  firstName: string;
  lastName: string;
  account: string;
  role: number;
  roleDesc?: string;
  status: number;
  statusDesc?: string;
  expiresTime: number;
  company: string;
  lang: string;
  workspaceId: string;
  token?: string;
  subscriptionPackageName?: string;
}

export interface UserInfo {
  data: IAuthUser;
}

class AuthUser {
  userJSON = (): IAuthUser => {
    return {
      account: "",
      company: "",
      expiresTime: 0,
      firstName: "",
      lang: "",
      lastName: "",
      role: 0,
      status: 0,
      token: "",
      workspaceId: "",
    };
  };

  setUser = (user: IAuthUser): IAuthUser => {
    return {
      account: user?.account,
      company: user?.company,
      expiresTime: user?.expiresTime,
      firstName: user?.firstName,
      lang: user?.lang,
      lastName: user?.lastName,
      role: user?.role,
      status: user?.status,
      token: user?.token,
      workspaceId: user?.workspaceId,
    };
  };

  logoutUser = (user: IAuthUser): IAuthUser => {
    return {
      account: "",
      company: "",
      expiresTime: 0,
      firstName: "",
      lang: user?.lang,
      lastName: "",
      role: 0,
      status: 0,
      token: "",
      workspaceId: "",
    };
  };
}

export const MyAuthUser = new AuthUser();
