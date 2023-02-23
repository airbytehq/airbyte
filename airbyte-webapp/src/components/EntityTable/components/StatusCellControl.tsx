import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Switch } from "components/ui/Switch";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { useEnableConnection, useSyncConnection } from "hooks/services/useConnectionHook";

import styles from "./StatusCellControl.module.scss";

interface StatusCellControlProps {
  hasBreakingChange?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  connection: WebBackendConnectionListItem;
}

export const StatusCellControl: React.FC<StatusCellControlProps> = ({
  enabled,
  isManual,
  id,
  isSyncing,
  hasBreakingChange,
  connection,
}) => {
  const { mutateAsync: enableConnection, isLoading } = useEnableConnection();
  const { mutateAsync: syncConnection, isLoading: isSyncStarting } = useSyncConnection();

  const onRunManualSync = (event: React.SyntheticEvent) => {
    event.stopPropagation();

    if (connection) {
      syncConnection(connection);
    }
  };

  if (!isManual) {
    const onSwitchChange = async (event: React.SyntheticEvent) => {
      event.stopPropagation();
      await enableConnection({
        connectionId: id,
        enable: !enabled,
      });
    };

    return (
      // this is so we can stop event propagation so the row doesn't receive the click and redirect
      // eslint-disable-next-line jsx-a11y/no-static-element-interactions
      <div
        onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
        onKeyPress={(event: React.SyntheticEvent) => event.stopPropagation()}
      >
        <Switch
          checked={enabled}
          onChange={onSwitchChange}
          disabled={hasBreakingChange}
          loading={isLoading}
          data-testid="enable-connection-switch"
        />
      </div>
    );
  }

  if (isSyncing) {
    return (
      <div className={styles.inProgressLabel}>
        <FormattedMessage id="connection.syncInProgress" />
      </div>
    );
  }

  return (
    <Button
      onClick={onRunManualSync}
      isLoading={isSyncStarting}
      disabled={!enabled || hasBreakingChange || isSyncStarting}
      data-testid="manual-sync-button"
    >
      <FormattedMessage id="connection.startSync" />
    </Button>
  );
};
