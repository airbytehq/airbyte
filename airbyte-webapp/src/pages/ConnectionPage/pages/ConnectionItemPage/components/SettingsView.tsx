import React from "react";

import DeleteBlock from "components/DeleteBlock";

import { useTrackPage } from "hooks/services/Analytics";
import { PAGE_TRACKING_CODES } from "hooks/services/Analytics/pageTrackingCodes";
import { useDeleteConnection } from "hooks/services/useConnectionHook";

import { WebBackendConnectionRead } from "../../../../../core/request/AirbyteClient";
import styles from "./SettingsView.module.scss";
import { StateBlock } from "./StateBlock";

interface SettingsViewProps {
  connection: WebBackendConnectionRead;
}

const SettingsView: React.FC<SettingsViewProps> = ({ connection }) => {
  const { mutateAsync: deleteConnection } = useDeleteConnection();

  useTrackPage(PAGE_TRACKING_CODES.CONNECTIONS_ITEM_SETTINGS);
  const onDelete = () => deleteConnection(connection);

  return (
    <div className={styles.container}>
      <StateBlock connectionId={connection.connectionId} />
      <DeleteBlock type="connection" onDelete={onDelete} />
    </div>
  );
};

export default SettingsView;
