import { AirbyteRequestService } from "../../core/request/AirbyteRequestService";

export interface Signup {
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface Signin {
  email: string;
  password: string;
}

export interface AuthenticatedUser {
  account: string;
  company: string;
  firstName: string;
  lang: string;
  lastName: string;
  token: string;
  workspaceId: string;
}

export function setAuthenticatedUser(userData: AuthenticatedUser) {
  localStorage.setItem("air-byte-user", JSON.stringify(userData));
}

export function getAuthenticatedUser() {
  return JSON.parse(localStorage.getItem("air-byte-user") as string);
}

export class AuthService extends AirbyteRequestService {
  public async create(signup: Signup): Promise<Signup> {
    return new Promise((resolve, reject) => {
      this.fetch<Signup>(`/user/register`, signup)
        .then((res: any) => {
          setAuthenticatedUser(res.data);
          resolve(res.data);
        })
        .catch((err: any) => {
          reject(err);
        });
    });
  }

  public async post(signin: Signin): Promise<Signin> {
    return new Promise((resolve, reject) => {
      this.fetch<Signin>(`/user/login`, signin)
        .then((res: any) => {
          setAuthenticatedUser(res.data);
          resolve(res.data);
        })
        .catch((err: any) => {
          reject(err);
        });
    });
  }
}
