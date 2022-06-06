import React, { useContext, useMemo, useState } from "react";
import { useDeepCompareEffect } from "react-use";

import { useConfig } from "config";

import { Feature, FeatureItem, FeatureServiceApi } from "./types";

const featureServiceContext = React.createContext<FeatureServiceApi | null>(null);

export const FeatureService = ({ children }: { children: React.ReactNode }) => {
  const [additionFeatures, setAdditionFeatures] = useState<Feature[]>([]);
  const { features: instanceWideFeatures } = useConfig();

  const featureMethods = useMemo(() => {
    return {
      registerFeature: (newFeatures: Feature[]): void =>
        setAdditionFeatures((oldFeatures) => [...oldFeatures, ...newFeatures]),
      unregisterFeature: (unregisteredFeatures: FeatureItem[]): void => {
        setAdditionFeatures((oldFeatures) =>
          oldFeatures.filter((feature) => !unregisteredFeatures.includes(feature.id))
        );
      },
    };
  }, []);

  const features = useMemo(
    () => [...instanceWideFeatures, ...additionFeatures],
    [instanceWideFeatures, additionFeatures]
  );

  const featureService = useMemo(
    () => ({
      features,
      hasFeature: (featureId: FeatureItem): boolean => !!features.find((feature) => feature.id === featureId),
      ...featureMethods,
    }),
    [features, featureMethods]
  );

  return <featureServiceContext.Provider value={featureService}>{children}</featureServiceContext.Provider>;
};

export const useFeatureService: () => FeatureServiceApi = () => {
  const featureService = useContext(featureServiceContext);
  if (!featureService) {
    throw new Error("useFeatureService must be used within a FeatureService.");
  }
  return featureService;
};

export const WithFeature: React.FC<{ featureId: FeatureItem }> = ({ featureId, children }) => {
  const { hasFeature } = useFeatureService();
  return hasFeature(featureId) ? <>{children}</> : null;
};

export const useFeatureRegisterValues = (props?: Feature[] | null): void => {
  const { registerFeature, unregisterFeature } = useFeatureService();

  useDeepCompareEffect(() => {
    if (!props) {
      return;
    }

    registerFeature(props);

    return () => unregisterFeature(props.map((feature: Feature) => feature.id));

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props]);
};
