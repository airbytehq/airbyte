import React from "react";

import DeleteBlock from "components/DeleteBlock";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useDeleteConnection } from "hooks/services/useConnectionHook";

import styles from "./ConnectionSettingsTab.module.scss";
import { StateBlock } from "./StateBlock";

export const ConnectionSettingsTab: React.FC = () => {
  const { connection } = useConnectionEditService();
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
