export enum FeatureItem {
  AllowUploadCustomImage = "ALLOW_UPLOAD_CUSTOM_IMAGE",
  AllowCustomDBT = "ALLOW_CUSTOM_DBT",
  AllowUpdateConnectors = "ALLOW_UPDATE_CONNECTORS",
  AllowOAuthConnector = "ALLOW_OAUTH_CONNECTOR",
  AllowCreateConnection = "ALLOW_CREATE_CONNECTION",
  AllowSync = "ALLOW_SYNC",
}

interface Feature {
  id: FeatureItem;
}

interface FeatureServiceApi {
  features: Feature[];
  registerFeature: (props: Feature[]) => void;
  unregisterFeature: (props: FeatureItem[]) => void;
  hasFeature: (featureId: FeatureItem) => boolean;
}

export type { Feature, FeatureServiceApi };
