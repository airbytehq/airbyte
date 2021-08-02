import React from "react";
import styled from "styled-components";

import WorkspaceItem from "./WorkspaceItem";
import WorkspacesControl from "./WorkspacesControl";

const Content = styled.div`
  width: 100%;
  max-width: 550px;
  margin: 0 auto;
`;

const WorkspacesList: React.FC = () => {
  //TODO: add real data
  const workspaces = [{ name: "Test", workspaceId: "test" }];
  return (
    <Content>
      {workspaces.length
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
