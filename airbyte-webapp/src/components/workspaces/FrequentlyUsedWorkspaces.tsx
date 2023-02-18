import { useEffect } from "react";
import { useIntl } from "react-intl";

import { Heading } from "components/ui/Heading";

import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import WorkspaceItem from "packages/cloud/views/workspaces/WorkspacesPage/components/WorkspaceItem";
import { useCurrentWorkspaceId, useWorkspaceService } from "services/workspaces/WorkspacesService";

import styles from "./FrequentlyUsedWorkspaces.module.scss";

interface FrequentlyUsedWorkspacesProps {
  workspaces: CloudWorkspace[];
}

const LOCAL_STORAGE_KEY = "ab_frequently_used_workspaces";

export const useTrackFrequentlyUsedWorkspaces = () => {
  const workspaceId = useCurrentWorkspaceId();

  useEffect(() => {
    if (workspaceId) {
      const previousWorkspaceIds = getFrequentlyUsedWorkspacesFromLocalStorage();
      const newWorkspaces = [workspaceId, ...previousWorkspaceIds.filter((id) => id !== workspaceId)].slice(0, 5);
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newWorkspaces));
    }
  }, [workspaceId]);
};

export function getFrequentlyUsedWorkspacesFromLocalStorage() {
  let frequentlyUsedWorkspaceIds: string[] = [];

  try {
    frequentlyUsedWorkspaceIds = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "[]");
    if (!Array.isArray(frequentlyUsedWorkspaceIds)) {
      throw new Error("Malformed localStorage item");
    }
  } catch {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    return [];
  }

  return frequentlyUsedWorkspaceIds;
}

export const FrequentlyUsedWorkspaces: React.FC<FrequentlyUsedWorkspacesProps> = ({ workspaces }) => {
  const { selectWorkspace } = useWorkspaceService();
  const { formatMessage } = useIntl();
  const frequentlyUsedWorkspaceIds = getFrequentlyUsedWorkspacesFromLocalStorage();
  const frequentlyUsedWorkspaces = workspaces.filter((workspace) =>
    frequentlyUsedWorkspaceIds.includes(workspace.workspaceId)
  );

  // In case one of the frequently used workspaces is no longer available
  if (frequentlyUsedWorkspaces.length === 0) {
    return null;
  }

  const sortedWorkspaces = frequentlyUsedWorkspaceIds.reduce<CloudWorkspace[]>((workspaces, id) => {
    const found = frequentlyUsedWorkspaces.find((workspace) => workspace.workspaceId === id);
    if (!found) {
      // Remove any IDs that cannot be resolved to a workspace
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(frequentlyUsedWorkspaceIds.filter((_id) => _id !== id)));
    } else {
      workspaces.push(found);
    }
    return workspaces;
  }, []);

  return (
    <div className={styles.frequentlyUsedWorkspaces}>
      <Heading as="h2" size="sm" className={styles.frequentlyUsedWorkspaces__heading}>
        {formatMessage({ id: "workspaces.frequentlyUsedWorkspacesTitle" })}
      </Heading>
      <div className={styles.frequentlyUsedWorkspaces__list}>
        {sortedWorkspaces.map((workspace) => (
          <WorkspaceItem key={workspace.workspaceId} id={workspace.workspaceId} onClick={selectWorkspace}>
            {workspace.name}
          </WorkspaceItem>
        ))}
      </div>
    </div>
  );
};
