import React from "react";

import { isSourceDefinitionSpecificationDraft } from "core/domain/connector/source";
import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useConnectorForm } from "views/Connector/ConnectorForm/connectorFormContext";

import { AuthButton } from "./AuthButton";
import { SectionContainer } from "../SectionContainer";

export const AuthSection: React.FC = () => {
  const { selectedConnectorDefinitionSpecification } = useConnectorForm();
  if (
    !selectedConnectorDefinitionSpecification ||
    isSourceDefinitionSpecificationDraft(selectedConnectorDefinitionSpecification)
  ) {
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
