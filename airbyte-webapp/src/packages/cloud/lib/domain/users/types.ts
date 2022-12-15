export type UserStatus = "invited" | "registered" | "disabled";

export interface User {
  email: string;
  name: string;
  authUserId: string;
  userId: string;
  status?: UserStatus;
  intercomHash: string;
}

export interface UserUpdate {
  userId: string;
  authUserId: string;
  name?: string;
  defaultWorkspaceId?: string;
  status?: UserStatus;
  email?: string;
  news?: boolean;
}
