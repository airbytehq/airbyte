import { UserInfo } from "../AuthContext/authenticatedUser";
import {
  UserPlanDetail,
  CreateSunscriptionUrl,
  GetUpgradeSubscriptionParams,
  UpgradeSubscription,
  PauseSubscription,
} from "../domain/payment";
import { ProductItemsList, PackagesDetail } from "../domain/product";
import { apiOverride } from "./apiOverride";

type SecondParameter<T extends (...args: any) => any> = T extends (config: any, args: infer P) => any ? P : never;

/**
 * @summary List all products registered in the current Daspire deployment
 */
export const userInfo = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<UserInfo>({ url: `/user/info`, method: "get" }, options);
};

/**
 * @summary List all products registered in the current Daspire deployment
 */
export const listProducts = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<ProductItemsList>({ url: `/product/item/rows`, method: "get" }, options);
};

export const packagesInfo = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<PackagesDetail>({ url: `/product/package/page/info`, method: "get" }, options);
};

/**
 * @summary payment apis in current Daspire deployment
 */
export const userPlan = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<UserPlanDetail>(
    {
      url: `/user/plan`,
      method: "post",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const createSubscription = (productItemId: string, options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<CreateSunscriptionUrl>(
    {
      url: `/sub/create?productItemId=${productItemId}`,
      method: "get",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const getUpgradeSubscription = (
  params: GetUpgradeSubscriptionParams,
  options?: SecondParameter<typeof apiOverride>
) => {
  return apiOverride<UpgradeSubscription>(
    {
      url: `/sub/get/upgrade?productItemId=${params.productItemId}&testProrationDate=${
        params?.testProrationDate ? params?.testProrationDate : ""
      }`,
      method: "get",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const upgradeSubscription = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<UpgradeSubscription>(
    {
      url: `/sub/upgrade`,
      method: "post",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const pauseSubscription = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<PauseSubscription>(
    {
      url: `/sub/pause`,
      method: "post",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};
