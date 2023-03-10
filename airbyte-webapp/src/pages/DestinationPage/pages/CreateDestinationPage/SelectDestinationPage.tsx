import React, { useState } from "react";
import { useIntl, FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";
import { ConnectionStep } from "components/ConnectionStep";
import DataPanel from "components/DataPanel";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorDefinition } from "core/domain/connector";
import { useAnalyticsService } from "hooks/services/Analytics";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

export interface ButtonItems {
  btnText: string;
  type: "cancel" | "disabled" | "active";
}

const Container = styled.div`
  max-width: 858px;
  margin: 0 auto 40px auto;
`;

const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
  );
};

const SelectDestinationCard: React.FC = () => {
  const { push, location } = useRouter();
  const { formatMessage } = useIntl();
  const analyticsService = useAnalyticsService();
  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string>(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : ""
  );

  const { destinationDefinitions } = useDestinationDefinitionList();

  const clickSelect = () => {
    if (!destinationDefinitionId) {
      return;
    }

    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);
    analyticsService.track(Namespace.DESTINATION, Action.SELECT, {
      actionDescription: "Destination connector type selected",
      connector_destination: connector?.name,
      connector_destination_definition_id: destinationDefinitionId,
    });

    push(`/${RoutePaths.Destination}/${RoutePaths.DestinationNew}`, {
      state: {
        destinationDefinitionId,
      },
    });
  };

  const afterSelect = (selectCardData: ConnectorDefinition) => {
    const selectId = Connector.id(selectCardData);
    if (destinationDefinitionId === selectId) {
      return setDestinationDefinitionId("");
    }
    setDestinationDefinitionId(selectId);
  };

  return (
    <>
      <ConnectionStep lightMode type="destination" />
      <Container>
        <DataPanel
          onSelect={afterSelect}
          data={destinationDefinitions}
          value={destinationDefinitionId}
          type="destination"
          title={formatMessage({
            id: "form.setup.destination",
          })}
        />
        <ButtonRows>
          <BigButton onClick={clickSelect} disabled={destinationDefinitionId ? false : true}>
            <FormattedMessage id="form.button.selectContinue" />
          </BigButton>
        </ButtonRows>
      </Container>
    </>
  );
};

export default SelectDestinationCard;
