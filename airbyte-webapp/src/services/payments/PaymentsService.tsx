import { useMutation } from "react-query";

import { useUser } from "core/AuthContext";
import { GetUpgradeSubscriptionParams, PaymentService } from "core/domain/payment";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const paymentKeys = {
  all: [SCOPE_USER, "payments"] as const,
  userPlanDetail: () => [...paymentKeys.all, "userPlanDetail"] as const,
  createSubscriptionUrl: (productItemId: string) =>
    [...paymentKeys.all, "createSubscriptionUrl", productItemId] as const,
};

function usePaymentService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new PaymentService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useUserPlanDetail = () => {
  const service = usePaymentService();

  return useSuspenseQuery(paymentKeys.userPlanDetail(), () => service.userPlanDetail()).data;
};

export const useCreateSubscription = () => {
  const service = usePaymentService();
  return useMutation((productItemId: string) => service.createSubscriptionUrl(productItemId));
};

export const useGetUpgradeSubscription = () => {
  const service = usePaymentService();
  return useMutation((params: GetUpgradeSubscriptionParams) => service.getUpgradeSubscription(params));
};

export const useUpgradeSubscription = () => {
  const service = usePaymentService();
  return useMutation(() => service.upgradeSubscription());
};

export const usePauseSubscription = () => {
  const service = usePaymentService();
  return useMutation(() => service.pauseSubscription());
};

export const useFailedPaymentDetails = () => {
  const service = usePaymentService();
  return useMutation(() => service.failedPaymentDetails());
};

export const useUpdatePaymentMethodURL = () => {
  const service = usePaymentService();
  return useMutation((paymentOrderId: string) => service.updatePaymentMethod(paymentOrderId));
};

export const useAsyncAction = (): {
  onCreateSubscriptionURL: (productItemId: string) => Promise<any>;
  onGetUpgradeSubscription: (params: GetUpgradeSubscriptionParams) => Promise<any>;
  onUpgradeSubscription: () => Promise<any>;
  onPauseSubscription: () => Promise<any>;
  onFailedPaymentDetails: () => Promise<any>;
  onUpdatePaymentMethodURL: (paymentOrderId: string) => Promise<any>;
} => {
  const { mutateAsync: createSubscription } = useCreateSubscription();
  const { mutateAsync: getUpgradeSubscription } = useGetUpgradeSubscription();
  const { mutateAsync: upgradeSubscription } = useUpgradeSubscription();
  const { mutateAsync: pauseSubscription } = usePauseSubscription();
  const { mutateAsync: failedPaymentDetails } = useFailedPaymentDetails();
  const { mutateAsync: updatePaymentMethodURL } = useUpdatePaymentMethodURL();

  const onCreateSubscriptionURL = async (productItemId: string) => {
    return await createSubscription(productItemId);
  };

  const onGetUpgradeSubscription = async (params: GetUpgradeSubscriptionParams) => {
    return await getUpgradeSubscription(params);
  };

  const onUpgradeSubscription = async () => {
    return await upgradeSubscription();
  };

  const onPauseSubscription = async () => {
    return await pauseSubscription();
  };

  const onFailedPaymentDetails = async () => {
    return await failedPaymentDetails();
  };

  const onUpdatePaymentMethodURL = async (paymentOrderId: string) => {
    return await updatePaymentMethodURL(paymentOrderId);
  };

  return {
    onCreateSubscriptionURL,
    onGetUpgradeSubscription,
    onUpgradeSubscription,
    onPauseSubscription,
    onFailedPaymentDetails,
    onUpdatePaymentMethodURL,
  };
};
