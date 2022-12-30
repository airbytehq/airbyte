import { UserInfo } from "../AuthContext/authenticatedUser";
import {
  UserPlanDetail,
  CreateSunscriptionUrl,
  GetUpgradeSubscriptionParams,
  UpgradeSubscription,
  PauseSubscription,
} from "../domain/payment";
import { ProductItemsList, PackagesDetail } from "../domain/product";
import { RolesList, UpdateRoleRequestBody } from "../domain/role";
import { UsersList, NewUser, NewUserRegisterBody } from "../domain/user";
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

/**
 * @summary role apis in current Daspire deployment
 */

export const listRoles = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<RolesList>({ url: `/user/management/role/list`, method: "get" }, options);
};

/**
 * @summary user management apis in current Daspire deployment
 */

export const listUser = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<UsersList>({ url: `/user/management/list`, method: "get" }, options);
};

export const addUsers = (users: NewUser[], options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<UsersList>(
    {
      url: `/user/management/add`,
      method: "post",
      headers: { "Content-Type": "application/json" },
      data: users,
    },
    options
  );
};

export const deleteUser = (userId: string, options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride(
    {
      url: `/user/management/del/${userId}`,
      method: "post",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const resendInviteToUser = (userId: string, options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride(
    {
      url: `/user/management/resend/${userId}`,
      method: "post",
      headers: { "Content-Type": "application/json" },
    },
    options
  );
};

export const updateUserRole = (
  UpdateRoleBody: UpdateRoleRequestBody,
  options?: SecondParameter<typeof apiOverride>
) => {
  return apiOverride(
    {
      url: `/user/management/edit/role`,
      method: "post",
      headers: { "Content-Type": "application/json" },
      data: UpdateRoleBody,
    },
    options
  );
};

export const registerNewUser = (
  newUserRegisterBody: NewUserRegisterBody,
  options?: SecondParameter<typeof apiOverride>
) => {
  return apiOverride(
    {
      url: `/user/management/register`,
      method: "post",
      headers: { "Content-Type": "application/json" },
      data: newUserRegisterBody,
    },
    options
  );
};
