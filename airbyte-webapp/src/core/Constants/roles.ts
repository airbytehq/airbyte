export const ROLES = {
  Administrator_Owner: "Administrator(owner)",
  Administrator: "Administrator",
  User: "User",
};

export const DASPIRE_ROLES = Object.values(ROLES);

export const getRoleAgainstRoleNumber = (role: number): string => {
  return DASPIRE_ROLES[role - 1];
};
