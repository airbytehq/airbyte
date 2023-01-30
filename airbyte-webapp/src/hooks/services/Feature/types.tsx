/**
 * FeatureItems are for permanent flags to differentiate features between environments (e.g. Cloud vs. OSS),
 * workspaces, specific user groups, etc.
 */

export enum FeatureItem {
  AllowAutoDetectSchema = "ALLOW_AUTO_DETECT_SCHEMA",
  AllowUploadCustomImage = "ALLOW_UPLOAD_CUSTOM_IMAGE",
  AllowCustomDBT = "ALLOW_CUSTOM_DBT",
  AllowDBTCloudIntegration = "ALLOW_DBT_CLOUD_INTEGRATION",
  AllowUpdateConnectors = "ALLOW_UPDATE_CONNECTORS",
  AllowOAuthConnector = "ALLOW_OAUTH_CONNECTOR",
  AllowSync = "ALLOW_SYNC",
  AllowChangeDataGeographies = "ALLOW_CHANGE_DATA_GEOGRAPHIES",
  AllowSyncSubOneHourCronExpressions = "ALLOW_SYNC_SUB_ONE_HOUR_CRON_EXPRESSIONS",
  FreeConnectorProgram = "FREE_CONNECTOR_PROGRAM",
}

export type FeatureSet = Partial<Record<FeatureItem, boolean>>;
