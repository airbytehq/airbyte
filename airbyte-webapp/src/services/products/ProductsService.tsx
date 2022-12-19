import { useUser } from "core/AuthContext";
import { PlanItemTypeEnum } from "core/domain/payment";
import { ProductService } from "core/domain/product";
import {
  PackageItem,
  ProcessedPackageMapItem,
  ProcessedProcessionalPackageMap,
  ProcessedEnterprisePackageMap,
} from "core/domain/product";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const productKeys = {
  all: [SCOPE_USER, "products"] as const,
  lists: () => [...productKeys.all, "list"] as const,
  packagesDetail: () => [...productKeys.all, "packagesDetail"] as const,
};

function useProductApiService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new ProductService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useListProducts = () => {
  const service = useProductApiService();
  return useSuspenseQuery(productKeys.lists(), () => service.list()).data;
};

export const usePackagesDetail = () => {
  const service = useProductApiService();

  return useSuspenseQuery(productKeys.packagesDetail(), () => service.packagesDetail()).data;
};

export const useProcessionalPackageMap = () => {
  const { Processional } = usePackagesDetail().packageMap;

  const processionalPackageMap: ProcessedProcessionalPackageMap = Processional.reduce(
    (acc_value: ProcessedProcessionalPackageMap, curr_value: PackageItem) => {
      if (curr_value.itemType === PlanItemTypeEnum.Features) {
        acc_value.processionalFeatures.push({ itemName: curr_value.itemName, processional: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Data_Replication) {
        acc_value.processionalDataReplication.push({ itemName: curr_value.itemName, processional: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Support) {
        acc_value.processionalSupport.push({ itemName: curr_value.itemName, processional: curr_value });
      } else {
        return acc_value;
      }
      return acc_value;
    },
    { processionalFeatures: [], processionalDataReplication: [], processionalSupport: [] }
  );

  return processionalPackageMap;
};

export const useEnterprisePackageMap = () => {
  const { Enterprise } = usePackagesDetail().packageMap;

  const enterprisePackageMap: ProcessedEnterprisePackageMap = Enterprise.reduce(
    (acc_value: ProcessedEnterprisePackageMap, curr_value: PackageItem) => {
      if (curr_value.itemType === PlanItemTypeEnum.Features) {
        acc_value.enterpriseFeatures.push({ itemName: curr_value.itemName, enterprise: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Data_Replication) {
        acc_value.enterpriseDataReplication.push({ itemName: curr_value.itemName, enterprise: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Support) {
        acc_value.enterpriseSupport.push({ itemName: curr_value.itemName, enterprise: curr_value });
      } else {
        return acc_value;
      }
      return acc_value;
    },
    { enterpriseFeatures: [], enterpriseDataReplication: [], enterpriseSupport: [] }
  );

  return enterprisePackageMap;
};

export const usePackagesMap = () => {
  const { processionalFeatures, processionalDataReplication, processionalSupport } = useProcessionalPackageMap();
  const { enterpriseFeatures, enterpriseDataReplication, enterpriseSupport } = useEnterprisePackageMap();

  const features = processionalFeatures.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseFeatures[i],
  }));
  const dataReplication = processionalDataReplication.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseDataReplication[i],
  }));
  const support = processionalSupport.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseSupport[i],
  }));

  return { features, dataReplication, support };
};
