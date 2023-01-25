import React from "react";
import { Navigate } from "react-router-dom";

import { DeleteBlock } from "components/common/DeleteBlock";
import { UpdateConnectionDataResidency } from "components/connection/UpdateConnectionDataResidency";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useDeleteConnection } from "hooks/services/useConnectionHook";

import styles from "./ConnectionSettingsPage.module.scss";
import { SchemaUpdateNotifications } from "./SchemaUpdateNotifications";
import { StateBlock } from "./StateBlock";

export const ConnectionSettingsPageInner: React.FC = () => {
  const { connection } = useConnectionEditService();
  const { mutateAsync: deleteConnection } = useDeleteConnection();
  const canUpdateDataResidency = useFeature(FeatureItem.AllowChangeDataGeographies);
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  const [isAdvancedMode] = useAdvancedModeSetting();
  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_SETTINGS);
  const onDelete = () => deleteConnection(connection);

  return (
    <div className={styles.container}>
      {allowAutoDetectSchema && <SchemaUpdateNotifications />}
      {canUpdateDataResidency && <UpdateConnectionDataResidency />}
      {isAdvancedMode && <StateBlock connectionId={connection.connectionId} />}
      <DeleteBlock type="connection" onDelete={onDelete} />
    </div>
  );
};

export const ConnectionSettingsPage: React.FC = () => {
  const { connection } = useConnectionEditService();
  const isConnectionDeleted = connection.status === ConnectionStatus.deprecated;

  return isConnectionDeleted ? <Navigate replace to=".." /> : <ConnectionSettingsPageInner />;
};
