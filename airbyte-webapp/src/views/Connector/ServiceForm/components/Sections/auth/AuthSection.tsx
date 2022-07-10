import React from "react";

import { FeatureItem, OnlyWithFeature } from "hooks/services/Feature";

import { SectionContainer } from "../common";
import { AuthButton } from "./AuthButton";

export const AuthSection: React.FC = () => {
  return (
    <OnlyWithFeature feature={FeatureItem.AllowOAuthConnector}>
      <SectionContainer>
        <AuthButton />
      </SectionContainer>
    </OnlyWithFeature>
  );
};
