import React from "react";

import { FeatureItem, WithFeature } from "hooks/services/Feature";

import { SectionContainer } from "../common";
import { AuthButton } from "./AuthButton";

export const AuthSection: React.FC = () => {
  return (
    <WithFeature featureId={FeatureItem.AllowOAuthConnector}>
      {
        <SectionContainer>
          <AuthButton />
        </SectionContainer>
      }
    </WithFeature>
  );
};
