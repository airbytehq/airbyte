import React from "react";
import { Button } from "components";

import { useConnectorAuth } from "hooks/services/useConnectorAuth";
import { ConnectorDefinitionSpecification } from "core/domain/connector";

type AuthButtonProps = {
  connector: ConnectorDefinitionSpecification;
};
export const AuthButton: React.FC<AuthButtonProps> = ({ connector }) => {
  const { getConsentUrl } = useConnectorAuth();

  return (
    <Button type="button" onClick={() => getConsentUrl(connector)}>
      Authenticate
    </Button>
  );
};
