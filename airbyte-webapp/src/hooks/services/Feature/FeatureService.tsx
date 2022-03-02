import React, { useContext, useEffect, useMemo, useState } from "react";
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
  const [additionFeatures, setAdditionFeatures] = useState<Feature[]>([]);
  const { features: mainFeatures } = useConfig();
  const features = useMemo(() => [...mainFeatures, ...additionFeatures], [
    mainFeatures,
    additionFeatures,
  ]);

  const featureService = useMemo(
    () => ({
      features,
      hasFeature: (featureId: FeatureItem): boolean =>
        !!features.find((feature) => feature.id === featureId),
      registerFeature: (newFeatures: Feature[]): void =>
        setAdditionFeatures([...additionFeatures, ...newFeatures]),
      unregisterFeature: (features: FeatureItem[]): void =>
        setAdditionFeatures(
          additionFeatures.filter((feature) => features.includes(feature.id))
        ),
    }),
    [features, additionFeatures, setAdditionFeatures]
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

export const useFeatureRegisterValues = (props?: Feature[] | null): void => {
  const { registerFeature, unregisterFeature } = useFeatureService();

  useEffect(() => {
    if (props) {
      registerFeature(props);

      return () =>
        unregisterFeature(props.map((feature: Feature) => feature.id));
    }

    return;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props]);
};
