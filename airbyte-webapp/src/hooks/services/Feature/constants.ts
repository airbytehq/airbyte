import { FeatureItem } from "./types";

/** The default feature set that OSS releases should use. */
export const defaultFeatures = [
  FeatureItem.AllowCreateConnection,
  FeatureItem.AllowCustomDBT,
  FeatureItem.AllowSync,
  FeatureItem.AllowUpdateConnectors,
  FeatureItem.AllowUploadCustomImage,
];
