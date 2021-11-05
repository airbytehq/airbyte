import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";
import { useServiceForm } from "../serviceFormContext";

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

export const AuthButton: React.FC = () => {
  const { selectedService, selectedConnector } = useServiceForm();
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { loading, done, run } = useRunOauthFlow(selectedConnector!);

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
            values={{ connector: selectedService?.name }}
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
