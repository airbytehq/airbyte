export enum FeatureItem {
  AllowUploadCustomImage = "ALLOW_UPLOAD_CUSTOM_IMAGE",
  AllowCustomDBT = "ALLOW_CUSTOM_DBT",
  AllowDBTCloudIntegration = "ALLOW_DBT_CLOUD_INTEGRATION",
  AllowUpdateConnectors = "ALLOW_UPDATE_CONNECTORS",
  AllowOAuthConnector = "ALLOW_OAUTH_CONNECTOR",
  AllowCreateConnection = "ALLOW_CREATE_CONNECTION",
  AllowSync = "ALLOW_SYNC",
  AllowSyncSubOneHourCronExpressions = "ALLOW_SYNC_SUB_ONE_HOUR_CRON_EXPRESSIONS",
}

export type FeatureSet = Record<FeatureItem, boolean>;
