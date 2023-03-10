export const ROLES = {
  Administrator_Owner: "Administrator(owner)",
  Administrator: "Administrator",
  User: "User",
};

export const ROLES_ZH = {
  Administrator_Owner: "管理者（账号所有者）",
  Administrator: "管理者",
  User: "普通用户",
};

export const DASPIRE_ROLES = Object.values(ROLES);

export const getRoleAgainstRoleNumber = (role: number): string => {
  return DASPIRE_ROLES[role - 1];
};
