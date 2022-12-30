export interface Role {
  desc: string;
  index: number;
}

export interface RolesList {
  data: Role[];
}

export interface UpdateRoleRequestBody {
  id: string;
  roleIndex: number;
}
