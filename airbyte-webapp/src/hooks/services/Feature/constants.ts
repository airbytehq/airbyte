import { FeatureItem } from "./types";

export const defaultOssFeatures = [
  FeatureItem.AllowAutoDetectSchema,
  FeatureItem.AllowCustomDBT,
  FeatureItem.AllowUpdateConnectors,
  FeatureItem.AllowUploadCustomImage,
  FeatureItem.AllowSyncSubOneHourCronExpressions,
];

export const defaultCloudFeatures = [
  FeatureItem.AllowAutoDetectSchema,
  FeatureItem.AllowOAuthConnector,
  FeatureItem.AllowChangeDataGeographies,
  FeatureItem.AllowDBTCloudIntegration,
  FeatureItem.FreeConnectorProgram,
];
