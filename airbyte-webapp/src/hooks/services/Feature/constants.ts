import { FeatureItem } from "./types";

export const defaultOssFeatures = [
  FeatureItem.AllowAutoDetectSchema,
  FeatureItem.AllowCustomDBT,
  FeatureItem.AllowSync,
  FeatureItem.AllowUpdateConnectors,
  FeatureItem.AllowUploadCustomImage,
  FeatureItem.AllowSyncSubOneHourCronExpressions,
];

export const defaultCloudFeatures = [
  FeatureItem.AllowAutoDetectSchema,
  FeatureItem.AllowOAuthConnector,
  FeatureItem.AllowSync,
  FeatureItem.AllowChangeDataGeographies,
  FeatureItem.AllowDBTCloudIntegration,
  FeatureItem.FreeConnectorProgram,
];
