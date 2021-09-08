type Feature = {
  id: string;
};

type FeatureServiceApi = {
  features: Feature[];
  hasFeature: (featureId: string) => boolean;
};

export type { Feature, FeatureServiceApi };
