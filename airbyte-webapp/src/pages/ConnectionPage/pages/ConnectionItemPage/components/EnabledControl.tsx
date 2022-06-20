import React from "react";
import { FormattedMessage } from "react-intl";
import { useUpdateEffect } from "react-use";
import styled from "styled-components";

import { Switch } from "components";

import { buildConnectionUpdate } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useUpdateConnection } from "hooks/services/useConnectionHook";

import { ConnectionStatus, WebBackendConnectionRead } from "../../../../../core/request/AirbyteClient";

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
  frequencyType?: string;
  onStatusUpdating?: (updating: boolean) => void;
}

const EnabledControl: React.FC<EnabledControlProps> = ({ connection, disabled, frequencyType, onStatusUpdating }) => {
  const { mutateAsync: updateConnection, isLoading } = useUpdateConnection();
  const analyticsService = useAnalyticsService();

  const onChangeStatus = async () => {
    await updateConnection(
      buildConnectionUpdate(connection, {
        status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
      })
    );

    analyticsService.track("Source - Action", {
      action: connection.status === ConnectionStatus.active ? "Disable connection" : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: frequencyType,
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
