import React from "react";

import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";

import { SectionContainer } from "../common";
import { AuthButton } from "./AuthButton";

export const AuthSection: React.FC = () => {
  return (
    <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
      <SectionContainer>
        <AuthButton />
      </SectionContainer>
    </IfFeatureEnabled>
  );
};
