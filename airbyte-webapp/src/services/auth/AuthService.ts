import { IAuthUser } from "core/AuthContext/authenticatedUser";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { userInfo } from "core/request/DaspireClient";

export interface Signup {
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthRead {
  data: IAuthUser;
}

export interface Signin {
  email: string;
  password: string;
}

export class AuthService extends AirbyteRequestService {
  public async create(signup: Signup, lang?: string): Promise<IAuthUser> {
    return new Promise((resolve, reject) => {
      this.fetch<AuthRead>(`/user/register`, signup, lang)
        .then((res: AuthRead) => {
          resolve(res.data);
        })
        .catch((err: Error) => {
          reject(err);
        });
    });
  }

  public async post(signin: Signin, lang?: string): Promise<IAuthUser> {
    return new Promise((resolve, reject) => {
      this.fetch<AuthRead>(`/user/login`, signin, lang)
        .then((res: AuthRead) => {
          resolve(res.data);
        })
        .catch((err: Error) => {
          reject(err);
        });
    });
  }

  public async googleAuth(token: string, lang?: string): Promise<IAuthUser> {
    return new Promise((resolve, reject) => {
      this.fetch<AuthRead>(`/user/third/oauth`, { accessToken: token, type: "GOOGLE" }, lang)
        .then((res: AuthRead) => {
          resolve(res.data);
        })
        .catch((err: Error) => {
          reject(err);
        });
    });
  }

  public async get(): Promise<IAuthUser> {
    return new Promise((resolve, reject) => {
      userInfo(this.requestOptions)
        .then((res: AuthRead) => {
          resolve(res.data);
        })
        .catch((err: Error) => {
          reject(err);
        });
    });
  }

  public userInfo() {
    return userInfo(this.requestOptions);
  }
}
