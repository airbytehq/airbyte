import React, { useContext, useMemo } from "react";
import { Feature, FeatureItem, FeatureServiceApi } from "./types";
import { useConfig } from "config";

const featureServiceContext = React.createContext<FeatureServiceApi | null>(
  null
);

export function FeatureService({
  children,
}: {
  children: React.ReactNode;
  features?: Feature[];
}) {
  const { features } = useConfig();
  const featureService = useMemo(
    () => ({
      features,
      hasFeature: (featureId: FeatureItem): boolean =>
        !!features.find((feature) => feature.id === featureId),
    }),
    [features]
  );

  return (
    <featureServiceContext.Provider value={featureService}>
      {children}
    </featureServiceContext.Provider>
  );
}

export const useFeatureService: () => FeatureServiceApi = () => {
  const featureService = useContext(featureServiceContext);
  if (!featureService) {
    throw new Error("useFeatureService must be used within a FeatureService.");
  }
  return featureService;
};

export const WithFeature: React.FC<{ featureId: FeatureItem }> = ({
  featureId,
  children,
}) => {
  const { hasFeature } = useFeatureService();
  return hasFeature(featureId) ? <>{children}</> : null;
};
