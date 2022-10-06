import React from "react";
import { FormattedMessage } from "react-intl";
import { useUpdateEffect } from "react-use";
import styled from "styled-components";

import { Switch } from "components/ui/Switch";

import { getScheduleInfo } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { buildConnectionUpdate } from "core/domain/connection";
import { ConnectionStatus, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useUpdateConnection } from "hooks/services/useConnectionHook";

const ToggleLabel = styled.label`
  text-transform: uppercase;
  font-size: 14px;
  line-height: 19px;
  font-weight: 500;
  color: ${({ theme }) => theme.greyColor40};
  display: inline-block;
  min-width: 75px;
  text-align: left;
  cursor: pointer;
`;

const Content = styled.div`
  display: flex;
  align-items: center;
`;

interface EnabledControlProps {
  connection: WebBackendConnectionRead;
  disabled?: boolean;
  onStatusUpdating?: (updating: boolean) => void;
}

const EnabledControl: React.FC<EnabledControlProps> = ({ connection, disabled, onStatusUpdating }) => {
  const { mutateAsync: updateConnection, isLoading } = useUpdateConnection();
  const analyticsService = useAnalyticsService();

  const onChangeStatus = async () => {
    await updateConnection(
      buildConnectionUpdate(connection, {
        status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
      })
    );

    const trackableAction = connection.status === ConnectionStatus.active ? Action.DISABLE : Action.REENABLE;

    analyticsService.track(Namespace.CONNECTION, trackableAction, {
      actionDescription: `${trackableAction} connection`,
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: getScheduleInfo(connection.scheduleData),
    });
  };

  useUpdateEffect(() => {
    onStatusUpdating?.(isLoading);
  }, [isLoading]);

  return (
    <Content>
      <ToggleLabel htmlFor="toggle-enabled-source">
        <FormattedMessage id={connection.status === ConnectionStatus.active ? "tables.enabled" : "tables.disabled"} />
      </ToggleLabel>
      <Switch
        disabled={disabled}
        onChange={onChangeStatus}
        checked={connection.status === ConnectionStatus.active}
        loading={isLoading}
        id="toggle-enabled-source"
      />
    </Content>
  );
};

export default EnabledControl;
