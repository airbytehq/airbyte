import { FeatureItem } from "./types";

export const defaultOssFeatures = [
  FeatureItem.AllowCustomDBT,
  FeatureItem.AllowSync,
  FeatureItem.AllowUpdateConnectors,
  FeatureItem.AllowUploadCustomImage,
  FeatureItem.AllowSyncSubOneHourCronExpressions,
];

export const defaultCloudFeatures = [
  FeatureItem.AllowOAuthConnector,
  FeatureItem.AllowSync,
  FeatureItem.AllowChangeDataGeographies,
  FeatureItem.AllowDBTCloudIntegration,
];
