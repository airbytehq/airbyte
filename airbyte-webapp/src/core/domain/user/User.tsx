export interface User {
  id: string;
  name: string;
  email: string;
  roleDesc: string;
  roleIndex: number;
  status: string;
}

export interface UsersList {
  data: User[];
}
