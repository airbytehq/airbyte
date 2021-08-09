import React, { useContext, useMemo } from "react";

const featureServiceContext = React.createContext<{
  features: [];
} | null>(null);

export function FeatureService({
  children,
  features,
}: {
  children: React.ReactNode;
  features: [];
}) {
  const featureService = useMemo(
    () => ({
      features,
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

export const useFeatureService: () => {
  features: [];
} = () => {
  const featureService = useContext(featureServiceContext);
  if (!featureService) {
    throw new Error("useFeatureService must be used within a FeatureService.");
  }
  return featureService;
};
