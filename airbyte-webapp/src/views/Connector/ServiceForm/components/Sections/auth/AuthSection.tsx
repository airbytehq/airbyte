import React from "react";

import { FormBlock } from "core/form/types";
import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";

import { SectionContainer } from "../common";
import { AuthButton } from "./AuthButton";
interface AuthSectionProps {
  authFormFields: FormBlock[];
}
export const AuthSection: React.FC<AuthSectionProps> = ({ authFormFields }) => {
  return (
    <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
      <SectionContainer>
        <AuthButton authFormFields={authFormFields} />
      </SectionContainer>
    </IfFeatureEnabled>
  );
};
