import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
} from "core/domain/connector";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";
import styled from "styled-components";

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

type AuthButtonProps = {
  connectorSpecification: ConnectorDefinitionSpecification;
  connector: ConnectorDefinition;
};

export const AuthButton: React.FC<AuthButtonProps> = ({
  connector,
  connectorSpecification,
}) => {
  const { loading, done, run } = useRunOauthFlow(connectorSpecification);
  return (
    <AuthSectionRow>
      <Button isLoading={loading} type="button" onClick={run}>
        {done ? (
          <>
            <FormattedMessage id="connectorForm.reauthenticate" />
          </>
        ) : (
          <FormattedMessage
            id="connectorForm.authenticate"
            values={{ connector: connector.name }}
          />
        )}
      </Button>
      {done && (
        <SuccessMessage>
          <FormattedMessage id="connectorForm.authenticate.succeeded" />
        </SuccessMessage>
      )}
    </AuthSectionRow>
  );
};
