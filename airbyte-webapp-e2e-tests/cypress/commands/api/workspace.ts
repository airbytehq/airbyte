let _workspaceId: string;

export const setWorkspaceId = (workspaceId: string) => {
  _workspaceId = workspaceId;
};

export const getWorkspaceId = () => {
  return _workspaceId;
};
