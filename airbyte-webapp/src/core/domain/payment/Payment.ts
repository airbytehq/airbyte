import { ProductItem } from "../product";

export const PlanItemTypeEnum = {
  Features: "Features",
  Data_Replication: "Data Replication",
  Support: "Support",
} as const;

export type PlanItemType = typeof PlanItemTypeEnum[keyof typeof PlanItemTypeEnum];

export interface PlanItem {
  planItemid: string;
  planItemType: PlanItemType;
  planItemTypeLang: string;
  planItemName: string;
  planItemScope: string | boolean;
  planItemScopeLang: string;
}

export interface PlanDetail {
  name: string;
  expiresTime: number;
  selectedProduct?: ProductItem;
  planDetail: PlanItem[];
}

export interface UserPlanDetail {
  data: PlanDetail;
}

export interface CreateSunscriptionUrl {
  data: string;
}

export interface GetUpgradeSubscriptionParams {
  productItemId: string;
  testProrationDate?: number;
}

export interface GetUpgradeSubscriptionDetail {
  totalDueToday: number;
  planName: string;
  productItemName: string;
  productItemPrice: number;
  expiresTime: number;
}

export interface UpgradeSubscription {
  data: GetUpgradeSubscriptionDetail;
}

export interface PauseSubscription {
  data: any;
}
