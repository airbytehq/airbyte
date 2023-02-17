import { useEffect, useState } from "react";
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
  const [frequentlyUsedWorkspaces, setFrequentlyUsedWorkspaces] = useState<string[]>(() => {
    const workspaces = localStorage.getItem(LOCAL_STORAGE_KEY);
    return workspaces ? JSON.parse(workspaces) : [];
  });
  const workspaceId = useCurrentWorkspaceId();

  useEffect(() => {
    if (workspaceId) {
      setFrequentlyUsedWorkspaces((previousWorkspaces) => {
        const newWorkspaces = [workspaceId, ...previousWorkspaces.filter((id) => id !== workspaceId)].slice(0, 5);
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newWorkspaces));
        return newWorkspaces;
      });
    }
  }, [frequentlyUsedWorkspaces, workspaceId]);
};

export const FrequentlyUsedWorkspaces: React.FC<FrequentlyUsedWorkspacesProps> = ({ workspaces }) => {
  const { selectWorkspace } = useWorkspaceService();
  const { formatMessage } = useIntl();
  let frequentlyUsedWorkspaceIds: string[];

  try {
    frequentlyUsedWorkspaceIds = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || "[]");
    if (!Array.isArray(frequentlyUsedWorkspaceIds)) {
      throw new Error("Malformed localStorage item");
    }
  } catch {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    return null;
  }

  // We should only show frequently used workspaces if the user has more than 10 available
  if (workspaces.length < 10 || frequentlyUsedWorkspaceIds.length === 0) {
    return null;
  }

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
      <Heading as="h2" size="sm">
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
