import React from "react";

import DeleteBlock from "components/DeleteBlock";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useDeleteConnection } from "hooks/services/useConnectionHook";

import styles from "./ConnectionSettingsTab.module.scss";
import { StateBlock } from "./StateBlock";

interface ConnectionSettingsTabProps {
  connection: WebBackendConnectionRead;
}

export const ConnectionSettingsTab: React.FC<ConnectionSettingsTabProps> = ({ connection }) => {
  const { mutateAsync: deleteConnection } = useDeleteConnection();

  const [isAdvancedMode] = useAdvancedModeSetting();
  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_SETTINGS);
  const onDelete = () => deleteConnection(connection);

  return (
    <div className={styles.container}>
      {isAdvancedMode && <StateBlock connectionId={connection.connectionId} />}
      <DeleteBlock type="connection" onDelete={onDelete} />
    </div>
  );
};
