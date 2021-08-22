import React, { useContext, useMemo } from "react";
import { Feature, FeatureServiceApi } from "./types";

const featureServiceContext = React.createContext<FeatureServiceApi | null>(
  null
);

export function FeatureService({
  children,
  features = [],
}: {
  children: React.ReactNode;
  features?: Feature[];
}) {
  const featureService = useMemo(
    () => ({
      features,
      hasFeature: (featureId: string): boolean =>
        !!features.find((feature) => feature.id === featureId),
    }),
    [features]
  );

  return (
    <>
      <featureServiceContext.Provider value={featureService}>
        {children}
      </featureServiceContext.Provider>
    </>
  );
}

export const useFeatureService: () => FeatureServiceApi = () => {
  const featureService = useContext(featureServiceContext);
  if (!featureService) {
    throw new Error("useFeatureService must be used within a FeatureService.");
  }
  return featureService;
};

export const WithFeature: React.FC<{ featureId: string }> = ({
  featureId,
  children,
}) => {
  const { hasFeature } = useFeatureService();
  return hasFeature(featureId) ? <>{children}</> : null;
};
