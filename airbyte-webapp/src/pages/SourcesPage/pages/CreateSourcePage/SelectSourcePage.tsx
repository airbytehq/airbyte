import React, { useState } from "react";
import { useIntl, FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";
import { ConnectionStep } from "components/ConnectionStep";
import DefinitionCard from "components/DataPanel";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorDefinition } from "core/domain/connector";
import { useAnalyticsService } from "hooks/services/Analytics";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

export interface ButtonItems {
  btnText: string;
  type: "cancel" | "disabled" | "active";
}

const Container = styled.div`
  max-width: 858px;
  margin: 0 auto 40px auto;
`;

const hasSourceDefinitionId = (state: unknown): state is { sourceDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { sourceDefinitionId?: string }).sourceDefinitionId === "string"
  );
};

const SelectNewSourceCard: React.FC = () => {
  const { push, location } = useRouter();
  const { formatMessage } = useIntl();
  const { sourceDefinitions } = useSourceDefinitionList();
  const analyticsService = useAnalyticsService();
  const [sourceDefinitionId, setSourceDefinitionId] = useState<string>(
    hasSourceDefinitionId(location.state) ? location.state.sourceDefinitionId : ""
  );

  const clickSelect = () => {
    push(`/${RoutePaths.Source}/${RoutePaths.SourceNew}`, {
      state: {
        sourceDefinitionId,
      },
    });

    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === sourceDefinitionId);
    analyticsService.track(Namespace.SOURCE, Action.SELECT, {
      actionDescription: "Source connector type selected",
      connector_source: connector?.name,
      connector_source_definition_id: sourceDefinitionId,
    });
  };

  const afterSelect = (selectCardData: ConnectorDefinition) => {
    const selectId = Connector.id(selectCardData);
    if (sourceDefinitionId === selectId) {
      return setSourceDefinitionId("");
    }
    setSourceDefinitionId(selectId);
  };
  return (
    <>
      <ConnectionStep lightMode type="source" />
      <Container>
        <DefinitionCard
          onSelect={afterSelect}
          data={sourceDefinitions}
          value={sourceDefinitionId}
          type="source"
          title={formatMessage({
            id: "form.setup.source",
          })}
        />
        <ButtonRows>
          <BigButton onClick={clickSelect} disabled={sourceDefinitionId ? false : true}>
            <FormattedMessage id="form.button.selectContinue" />
          </BigButton>
        </ButtonRows>
      </Container>
    </>
  );
};

export default SelectNewSourceCard;
