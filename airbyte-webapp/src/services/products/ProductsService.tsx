import { useUser } from "core/AuthContext";
import { PlanItemTypeEnum } from "core/domain/payment";
import { ProductService, ProductOptionItem } from "core/domain/product";
import {
  PackageItem,
  ProcessedPackageMapItem,
  ProcessedProfessionalPackageMap,
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

const setFunctionValue = (label: string): number => {
  switch (label) {
    case "1M":
      return 1;

    case "2M":
      return 6;

    case "3M":
      return 11;

    case "5M":
      return 17;

    case "10M":
      return 28;

    case "20M":
      return 45;

    case "50M":
      return 65;

    case "100M":
      return 93;

    default:
      return 0;
  }
};

export const useProductOptions = (): ProductOptionItem[] => {
  const products = useListProducts();

  const productOptions: ProductOptionItem[] = products.map((product) => {
    return {
      id: product.id,
      itemName: product.itemName,
      value: setFunctionValue(product.itemName),
      label: product.itemName,
      price: `${product.price}`,
    };
  });

  const customProduct: ProductOptionItem = {
    id: "",
    itemName: "",
    value: 100,
    label: "",
    price: "custom",
  };

  return [...productOptions, customProduct];
};

export const usePackagesDetail = () => {
  const service = useProductApiService();

  return useSuspenseQuery(productKeys.packagesDetail(), () => service.packagesDetail()).data;
};

export const useProfessionalPackageMap = () => {
  const { Professional } = usePackagesDetail().packageMap;

  const professionalPackageMap: ProcessedProfessionalPackageMap = Professional.reduce(
    (acc_value: ProcessedProfessionalPackageMap, curr_value: PackageItem) => {
      if (curr_value.itemType === PlanItemTypeEnum.Features) {
        acc_value.professionalFeatures.push({ itemName: curr_value.itemName, professional: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Data_Replication) {
        acc_value.professionalDataReplication.push({ itemName: curr_value.itemName, professional: curr_value });
      } else if (curr_value.itemType === PlanItemTypeEnum.Support) {
        acc_value.professionalSupport.push({ itemName: curr_value.itemName, professional: curr_value });
      } else {
        return acc_value;
      }
      return acc_value;
    },
    { professionalFeatures: [], professionalDataReplication: [], professionalSupport: [] }
  );

  return professionalPackageMap;
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
  const { professionalFeatures, professionalDataReplication, professionalSupport } = useProfessionalPackageMap();
  const { enterpriseFeatures, enterpriseDataReplication, enterpriseSupport } = useEnterprisePackageMap();

  const features = professionalFeatures.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseFeatures[i],
  }));
  const dataReplication = professionalDataReplication.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseDataReplication[i],
  }));
  const support = professionalSupport.map((item: ProcessedPackageMapItem, i: number) => ({
    ...item,
    ...enterpriseSupport[i],
  }));

  return { features, dataReplication, support };
};
