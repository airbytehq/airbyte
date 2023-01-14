import classNames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";

import { Switch } from "components/ui/Switch";

import { Action, Namespace } from "core/analytics";
import { getFrequencyFromScheduleData } from "core/analytics/utils";
import { ConnectionStatus } from "core/request/AirbyteClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";

import styles from "./EnabledControl.module.scss";

interface EnabledControlProps {
  disabled?: boolean;
}

export const EnabledControl: React.FC<EnabledControlProps> = ({ disabled }) => {
  const analyticsService = useAnalyticsService();

  const { connection, updateConnection, connectionUpdating } = useConnectionEditService();

  const [{ loading }, onChangeStatus] = useAsyncFn(async () => {
    await updateConnection({
      connectionId: connection.connectionId,
      status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
    });

    const trackableAction = connection.status === ConnectionStatus.active ? Action.DISABLE : Action.REENABLE;

    analyticsService.track(Namespace.CONNECTION, trackableAction, {
      actionDescription: `${trackableAction} connection`,
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: getFrequencyFromScheduleData(connection.scheduleData),
    });
  }, [
    analyticsService,
    connection.connectionId,
    connection.destination?.destinationDefinitionId,
    connection.destination?.destinationName,
    connection.source?.sourceDefinitionId,
    connection.source?.sourceName,
    connection.status,
    updateConnection,
  ]);

  const isSwitchDisabled = disabled || connectionUpdating;

  return (
    <div className={styles.container} data-testid="enabledControl">
      <label
        htmlFor="toggle-enabled-source"
        className={classNames(styles.label, { [styles.disabled]: isSwitchDisabled })}
      >
        <FormattedMessage id={connection.status === ConnectionStatus.active ? "tables.enabled" : "tables.disabled"} />
      </label>
      <Switch
        disabled={isSwitchDisabled}
        onChange={onChangeStatus}
        checked={connection.status === ConnectionStatus.active}
        loading={loading}
        id="toggle-enabled-source"
        data-testid="enabledControl-switch"
      />
    </div>
  );
};
