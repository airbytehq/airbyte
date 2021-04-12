import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Toggle from "components/Toggle";
import { Connection } from "core/resources/Connection";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import config from "config";
import useConnection from "components/hooks/services/useConnectionHook";

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
  connection: Connection;
  frequencyText?: string;
};

const EnabledControl: React.FC<IProps> = ({ connection, frequencyText }) => {
  const { updateConnection } = useConnection();

  const onChangeStatus = async () => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      schedule: connection.schedule,
      prefix: connection.prefix,
      status: connection.status === "active" ? "inactive" : "active",
    });

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action:
        connection.status === "active"
          ? "Disable connection"
          : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequencyText,
    });
  };

  return (
    <Content>
      <ToggleLabel htmlFor="toggle-enabled-source">
        <FormattedMessage
          id={
            connection.status === "active"
              ? "tables.enabled"
              : "tables.disabled"
          }
        />
      </ToggleLabel>
      <Toggle
        onChange={onChangeStatus}
        checked={connection.status === "active"}
        id="toggle-enabled-source"
      />
    </Content>
  );
};

export default EnabledControl;
