import React, { useCallback, useContext, useMemo, useState } from "react";

import { FeatureItem, FeatureSet } from "./types";

interface FeatureServiceContext {
  features: FeatureItem[];
  setWorkspaceFeatures: (features: FeatureItem[] | FeatureSet | undefined) => void;
  setUserFeatures: (features: FeatureItem[] | FeatureSet | undefined) => void;
  setFeatureOverwrites: (features: FeatureItem[] | FeatureSet | undefined) => void;
}

const featureServiceContext = React.createContext<FeatureServiceContext | null>(null);

const featureSetFromList = (featureList: FeatureItem[]): FeatureSet => {
  return featureList.reduce((set, val) => ({ ...set, [val]: true }), {} as FeatureSet);
};

interface FeatureServiceProps {
  features: FeatureItem[];
}

/**
 * The FeatureService allows tracking support for whether a specific feature should be
 * enabled or disabled. The feature can be enabled/disabled on either of the following level:
 *
 * - globally (the values passed into this service)
 * - workspace (can be configured via setWorkspaceFeatures)
 * - user (can be configured via setUserFeatures)
 *
 * In addition via setFeatureOverwrites allow overwriting any features. The priority for configuring
 * features is: overwrite > user > workspace > globally, i.e. if a feature is disabled for a user
 * it will take precedence over the feature being enabled globally or for that workspace.
 */
export const FeatureService: React.FC<FeatureServiceProps> = ({ features: defaultFeatures, children }) => {
  const [workspaceFeatures, setWorkspaceFeaturesState] = useState<FeatureSet>();
  const [userFeatures, setUserFeaturesState] = useState<FeatureSet>();
  const [overwrittenFeatures, setOverwrittenFeaturesState] = useState<FeatureSet>();

  const combinedFeatures = useMemo(() => {
    const combined: FeatureSet = {
      ...featureSetFromList(defaultFeatures),
      ...workspaceFeatures,
      ...userFeatures,
      ...overwrittenFeatures,
    };

    return Object.entries(combined)
      .filter(([, enabled]) => enabled)
      .map(([id]) => id) as FeatureItem[];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceFeatures, userFeatures, overwrittenFeatures, ...defaultFeatures]);

  const setWorkspaceFeatures = useCallback((features: FeatureItem[] | FeatureSet | undefined) => {
    setWorkspaceFeaturesState(Array.isArray(features) ? featureSetFromList(features) : features);
  }, []);

  const setUserFeatures = useCallback((features: FeatureItem[] | FeatureSet | undefined) => {
    setUserFeaturesState(Array.isArray(features) ? featureSetFromList(features) : features);
  }, []);

  const setFeatureOverwrites = useCallback((features: FeatureItem[] | FeatureSet | undefined) => {
    setOverwrittenFeaturesState(Array.isArray(features) ? featureSetFromList(features) : features);
  }, []);

  const serviceContext = useMemo(
    (): FeatureServiceContext => ({
      features: combinedFeatures,
      setWorkspaceFeatures,
      setUserFeatures,
      setFeatureOverwrites,
    }),
    [combinedFeatures, setFeatureOverwrites, setUserFeatures, setWorkspaceFeatures]
  );

  return <featureServiceContext.Provider value={serviceContext}>{children}</featureServiceContext.Provider>;
};

export const useFeatureService: () => FeatureServiceContext = () => {
  const featureService = useContext(featureServiceContext);
  if (!featureService) {
    throw new Error("useFeatureService must be used within a FeatureService.");
  }
  return featureService;
};

/**
 * Returns whether a specific feature is enabled currently.
 * Will cause the component to rerender if the state of the feature changes.
 */
export const useFeature = (feature: FeatureItem): boolean => {
  const { features } = useFeatureService();
  return features.includes(feature);
};

export const IfFeatureEnabled: React.FC<{ feature: FeatureItem }> = ({ feature, children }) => {
  const hasFeature = useFeature(feature);
  return hasFeature ? <>{children}</> : null;
};
