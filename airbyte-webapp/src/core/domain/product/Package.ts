import { ProductItem } from "./Product";

export interface PackageItem {
  packageName: string;
  itemType: string;
  itemName: string;
  itemScope: string;
}

export interface ProcessedPackageMapItem {
  itemName: string;
  processional?: PackageItem;
  enterprise?: PackageItem;
}

export interface ProcessedProcessionalPackageMap {
  processionalFeatures: ProcessedPackageMapItem[];
  processionalDataReplication: ProcessedPackageMapItem[];
  processionalSupport: ProcessedPackageMapItem[];
}

export interface ProcessedEnterprisePackageMap {
  enterpriseFeatures: ProcessedPackageMapItem[];
  enterpriseDataReplication: ProcessedPackageMapItem[];
  enterpriseSupport: ProcessedPackageMapItem[];
}

export interface ProcessedPackageMap {
  features: ProcessedPackageMapItem[];
  dataReplication: ProcessedPackageMapItem[];
  support: ProcessedPackageMapItem[];
}

export interface PackageMap {
  Processional: PackageItem[];
  Enterprise: PackageItem[];
}

export interface PackagesInfo {
  userSubscriptionProductItemId: string | null;
  status: number;
  productItem: ProductItem[];
  packageMap: PackageMap;
}

export interface PackagesDetail {
  data: PackagesInfo;
}
