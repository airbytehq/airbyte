import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Toggle } from "components";

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

type IProps = {
  connection: WebBackendConnectionRead;
  disabled?: boolean;
  frequencyText?: string;
};

const EnabledControl: React.FC<IProps> = ({ connection, disabled, frequencyText }) => {
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const analyticsService = useAnalyticsService();

  const onChangeStatus = async () => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      schedule: connection.schedule,
      namespaceDefinition: connection.namespaceDefinition,
      namespaceFormat: connection.namespaceFormat,
      prefix: connection.prefix,
      operations: connection.operations,
      status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
    });

    analyticsService.track("Source - Action", {
      action: connection.status === ConnectionStatus.active ? "Disable connection" : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: frequencyText,
    });
  };

  return (
    <Content>
      <ToggleLabel htmlFor="toggle-enabled-source">
        <FormattedMessage id={connection.status === ConnectionStatus.active ? "tables.enabled" : "tables.disabled"} />
      </ToggleLabel>
      <Toggle
        disabled={disabled}
        onChange={onChangeStatus}
        checked={connection.status === ConnectionStatus.active}
        id="toggle-enabled-source"
      />
    </Content>
  );
};

export default EnabledControl;
