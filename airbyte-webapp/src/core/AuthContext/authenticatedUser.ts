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
}

export const MyAuthUser = new AuthUser();
