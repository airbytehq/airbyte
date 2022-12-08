export const ROLES = {
  "Administrator(owner)": "Administrator(owner)",
  Administrator: "Administrator",
  User: "User",
};

export const DASPIRE_ROLES = Object.values(ROLES);

export const getRoleAgainstRoleNumber = (roleNumber: number): string => {
  return DASPIRE_ROLES[roleNumber - 1];
};
