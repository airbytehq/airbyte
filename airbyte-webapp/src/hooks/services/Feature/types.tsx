export enum FeatureItem {
  AllowUploadCustomImage = "ALLOW_UPLOAD_CUSTOM_IMAGE",
  AllowCustomDBT = "ALLOW_CUSTOM_DBT",
  AllowUpdateConnectors = "ALLOW_UPDATE_CONNECTORS",
  AllowOAuthConnector = "ALLOW_OAUTH_CONNECTOR",
}

type Feature = {
  id: FeatureItem;
};

type FeatureServiceApi = {
  features: Feature[];
  hasFeature: (featureId: string) => boolean;
};

export type { Feature, FeatureServiceApi };
