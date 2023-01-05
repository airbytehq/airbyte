import React from "react";

import { isSourceDefinitionSpecificationDraft } from "core/domain/connector/source";
import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useConnectorForm } from "views/Connector/ConnectorForm/connectorFormContext";

import { SectionContainer } from "../SectionContainer";
import { AuthButton } from "./AuthButton";

export const AuthSection: React.FC = () => {
  const { selectedConnectorDefinitionSpecification } = useConnectorForm();
  if (isSourceDefinitionSpecificationDraft(selectedConnectorDefinitionSpecification)) {
    return null;
  }
  return (
    <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
      <SectionContainer>
        <AuthButton selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification} />
      </SectionContainer>
    </IfFeatureEnabled>
  );
};
