export interface NewUser {
  email: string;
  role: number;
}

export interface NewUserRegisterBody {
  firstName: string;
  lastName: string;
  invitedId: string;
  password: string;
  confirmPassword: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  roleDesc: string;
  roleIndex: number;
  status: string;
  statusLang: string;
}

export interface UsersList {
  data: User[];
}
