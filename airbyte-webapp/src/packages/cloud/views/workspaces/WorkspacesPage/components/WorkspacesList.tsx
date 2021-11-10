import React from "react";
import styled from "styled-components";

import WorkspaceItem from "./WorkspaceItem";
import WorkspacesControl from "./WorkspacesControl";
import {
  useListWorkspaces,
  useWorkspaceService,
} from "packages/cloud/services/workspaces/WorkspacesService";

const Content = styled.div`
  width: 100%;
  max-width: 550px;
  margin: 0 auto;
  padding-bottom: 26px;
`;

const WorkspacesList: React.FC = () => {
  const { data: workspaces } = useListWorkspaces();
  const { selectWorkspace, createWorkspace } = useWorkspaceService();

  return (
    <Content>
      {workspaces?.length
        ? workspaces.map((workspace) => (
            <WorkspaceItem
              key={workspace.workspaceId}
              id={workspace.workspaceId}
              onClick={selectWorkspace}
            >
              {workspace.name}
            </WorkspaceItem>
          ))
        : null}
      <WorkspacesControl onSubmit={createWorkspace} />
    </Content>
  );
};

export default WorkspacesList;
