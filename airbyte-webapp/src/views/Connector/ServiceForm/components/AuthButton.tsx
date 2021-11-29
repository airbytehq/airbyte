import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { useRunOauthFlow } from "hooks/services/useConnectorAuth";
import { useServiceForm } from "../serviceFormContext";
import { Button } from "components/base/Button";
import { isSourceDefinition } from "core/domain/connector/source";
import { ConnectorDefinition } from "core/domain/connector";
import { isDestinationDefinition } from "core/domain/connector/destination";
import GoogleAuthButton from "./GoogleAuthButton";

const AuthSectionRow = styled.div`
  display: flex;
  align-items: center;
`;

const SuccessMessage = styled.div`
  color: ${({ theme }) => theme.successColor};
  font-style: normal;
  font-weight: normal;
  font-size: 14px;
  line-height: 17px;
  margin-left: 14px;
`;

function isGoogleConnector(connectorDefinitionId: string): boolean {
  return [
    "253487c0-2246-43ba-a21f-5116b20a2c50", // google ads
    "eff3616a-f9c3-11eb-9a03-0242ac130003", // google analytics
    "d19ae824-e289-4b14-995a-0632eb46d246", // google directory
    "eb4c9e00-db83-4d63-a386-39cfa91012a8", // google search console
    "71607ba1-c0ac-4799-8049-7f4b90dd50f7", // google sheets
    "ed9dfefa-1bbc-419d-8c5e-4d78f0ef6734", // google workspace admin reports
  ].includes(connectorDefinitionId);
}

function getDefinitionId(
  connectorDefinition: ConnectorDefinition
): string | undefined {
  if (connectorDefinition && isSourceDefinition(connectorDefinition)) {
    return connectorDefinition.sourceDefinitionId;
  } else if (
    connectorDefinition &&
    isDestinationDefinition(connectorDefinition)
  ) {
    return connectorDefinition.destinationDefinitionId;
  } else {
    console.error(
      "Could not find connector definition ID -- this is probably a programmer error"
    );
    return;
  }
}

function getButtonComponent(connectorDefinitionId: string) {
  if (isGoogleConnector(connectorDefinitionId)) {
    return GoogleAuthButton;
  } else {
    return Button;
  }
}

function getAuthenticateMessageId(connectorDefinitionId: string) {
  if (isGoogleConnector(connectorDefinitionId)) {
    return "connectorForm.signInWithGoogle";
  } else {
    return "connectorForm.authenticate";
  }
}

export const AuthButton: React.FC = () => {
  const { selectedService, selectedConnector } = useServiceForm();
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { loading, done, run } = useRunOauthFlow(selectedConnector!);
  const definitionId = getDefinitionId(selectedService!);
  const Component = getButtonComponent(definitionId!);
  return (
    <AuthSectionRow>
      <Component isLoading={loading} type="button" onClick={run}>
        {done ? (
          <FormattedMessage id="connectorForm.reauthenticate" />
        ) : (
          <FormattedMessage
            id={getAuthenticateMessageId(definitionId!)}
            values={{ connector: selectedService?.name }}
          />
        )}
      </Component>
      {done && (
        <SuccessMessage>
          <FormattedMessage id="connectorForm.authenticate.succeeded" />
        </SuccessMessage>
      )}
    </AuthSectionRow>
  );
};
