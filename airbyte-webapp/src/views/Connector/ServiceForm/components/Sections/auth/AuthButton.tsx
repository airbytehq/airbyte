import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { ConnectorSpecification } from "core/domain/connector";

import { useServiceForm } from "../../../serviceFormContext";
import GoogleAuthButton from "./GoogleAuthButton";
import { useFormikOauthAdapter } from "./useOauthFlowAdapter";

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
    "71607ba1-c0ac-4799-8049-7f4b90dd50f7", // google sheets source
    "a4cbd2d1-8dbe-4818-b8bc-b90ad782d12a", // google sheets destination
    "ed9dfefa-1bbc-419d-8c5e-4d78f0ef6734", // google workspace admin reports
  ].includes(connectorDefinitionId);
}

function getButtonComponent(connectorDefinitionId: string) {
  if (isGoogleConnector(connectorDefinitionId)) {
    return GoogleAuthButton;
  }
  return Button;
}

function getAuthenticateMessageId(connectorDefinitionId: string): string {
  if (isGoogleConnector(connectorDefinitionId)) {
    return "connectorForm.signInWithGoogle";
  }
  return "connectorForm.authenticate";
}

export const AuthButton: React.FC = () => {
  const { selectedService, selectedConnector } = useServiceForm();
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { loading, done, run } = useFormikOauthAdapter(selectedConnector!);

  if (!selectedConnector) {
    console.error("Entered non-auth flow while no connector is selected");
    return null;
  }

  const definitionId = ConnectorSpecification.id(selectedConnector);
  const Component = getButtonComponent(definitionId);
  return (
    <AuthSectionRow>
      <Component isLoading={loading} type="button" onClick={() => run()}>
        {done ? (
          <FormattedMessage id="connectorForm.reauthenticate" />
        ) : (
          <FormattedMessage id={getAuthenticateMessageId(definitionId)} values={{ connector: selectedService?.name }} />
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
