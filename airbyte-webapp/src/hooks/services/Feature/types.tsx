export enum FeatureItem {
  AllowUploadCustomImage = "ALLOW_UPLOAD_CUSTOM_IMAGE",
  AllowCustomDBT = "ALLOW_CUSTOM_DBT",
  AllowUpdateConnectors = "ALLOW_UPDATE_CONNECTORS",
  AllowOAuthConnector = "ALLOW_OAUTH_CONNECTOR",
  AllowCreateConnection = "ALLOW_CREATE_CONNECTION",
  AllowSync = "ALLOW_SYNC",
}

export type FeatureSet = Record<FeatureItem, boolean>;
