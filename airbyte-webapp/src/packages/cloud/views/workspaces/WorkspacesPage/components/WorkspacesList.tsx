import React from "react";
import styled from "styled-components";

import WorkspaceItem from "./WorkspaceItem";
import WorkspacesControl from "./WorkspacesControl";
import { useListWorkspaces } from "packages/cloud/services/workspaces/WorkspacesService";

const Content = styled.div`
  width: 100%;
  max-width: 550px;
  margin: 0 auto;
`;

const WorkspacesList: React.FC = () => {
  const { data: workspaces } = useListWorkspaces();

  return (
    <Content>
      {workspaces?.length
        ? workspaces.map((workspace) => (
            <WorkspaceItem key={workspace.workspaceId}>
              {workspace.name}
            </WorkspaceItem>
          ))
        : null}
      <WorkspacesControl />
    </Content>
  );
};

export default WorkspacesList;
