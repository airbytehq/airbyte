import React from "react";
import { useIntl } from "react-intl";

import { Heading } from "components/ui/Heading";
import {
  FrequentlyUsedWorkspaces,
  getFrequentlyUsedWorkspacesFromLocalStorage,
} from "components/workspaces/FrequentlyUsedWorkspaces";

import {
  useCreateCloudWorkspace,
  useListCloudWorkspaces,
} from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useWorkspaceService } from "services/workspaces/WorkspacesService";

import WorkspaceItem from "./WorkspaceItem";
import WorkspacesControl from "./WorkspacesControl";
import styles from "./WorkspacesList.module.scss";

const WorkspacesList: React.FC = () => {
  const workspaces = useListCloudWorkspaces();
  const { selectWorkspace } = useWorkspaceService();
  const { mutateAsync: createCloudWorkspace } = useCreateCloudWorkspace();
  const { formatMessage } = useIntl();
  const showFrequentlyUsedWorkspaces =
    workspaces.length >= 10 && getFrequentlyUsedWorkspacesFromLocalStorage().length > 0;

  return (
    <div className={styles.workspacesList}>
      {showFrequentlyUsedWorkspaces && <FrequentlyUsedWorkspaces workspaces={workspaces} />}
      {showFrequentlyUsedWorkspaces && (
        <Heading as="h2" size="sm" className={styles.workspacesList__heading}>
          {formatMessage({ id: "workspaces.allWorkspacesListHeader" })}
        </Heading>
      )}
      {workspaces.map((workspace) => (
        <WorkspaceItem key={workspace.workspaceId} id={workspace.workspaceId} onClick={selectWorkspace}>
          {workspace.name}
        </WorkspaceItem>
      ))}
      <WorkspacesControl onSubmit={createCloudWorkspace} />
    </div>
  );
};

export default WorkspacesList;
