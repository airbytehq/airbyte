import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";
import HeadTitle from "components/HeadTitle";
import MainPageWithScroll from "components/MainPageWithScroll";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import { CreateSunscriptionUrl, GetUpgradeSubscriptionDetail, UpgradeSubscription } from "core/domain/payment";
import { ProductOptionItem } from "core/domain/product";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";
import { useAsyncAction, useUserPlanDetail } from "services/payments/PaymentsService";
import { useProductOptions, usePackagesMap } from "services/products/ProductsService";

import PaymentNav from "./components/PaymentNav";
import styles from "./PaymentPage.module.scss";
import BillingPaymentStep from "./steps/BillingPaymentStep";
import SelectPlanStep from "./steps/SelectPlanStep";

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainView = styled.div`
  width: 100%;
`;

export const PaymentSteps = {
  SELECT_PLAN: "SELECT_PLAN",
  BILLING_PAYMENT: "BILLING_PAYMENT",
} as const;

const PaymentPage: React.FC = () => {
  const { push } = useRouter();

  const [currentStep, setCurrentStep] = useState<string>(PaymentSteps.SELECT_PLAN);
  const [product, setProduct] = useState<ProductOptionItem | undefined>();
  const [paymentLoading, setPaymentLoading] = useState<boolean>(false);
  const [planDetail, setPlanDetail] = useState<GetUpgradeSubscriptionDetail>();
  const [updatePlanLoading, setUpdatePlanLoading] = useState<boolean>(false);

  const authService = useAuthenticationService();
  const { onCreateSubscriptionURL, onGetUpgradeSubscription, onUpgradeSubscription } = useAsyncAction();

  const { updateUserStatus, user } = useUser();
  const userPlanDetail = useUserPlanDetail();
  const { selectedProduct } = userPlanDetail;
  const packagesMap = usePackagesMap();
  const productOptions = useProductOptions();

  useEffect(() => {
    if (!selectedProduct && product === undefined) {
      setProduct(productOptions[1]);
    }
  }, [selectedProduct, productOptions, product]);

  useEffect(() => {
    if (selectedProduct && product === undefined) {
      let index = -1;
      index = productOptions.findIndex((option) => option.id === selectedProduct.id);
      if (index >= 0) {
        setProduct(productOptions[index]);
      }
    }
  }, [productOptions, selectedProduct, product]);

  const onSelectPlan = useCallback(async () => {
    setPaymentLoading(true);
    if (
      getPaymentStatus(user.status) === PAYMENT_STATUS.Subscription ||
      getPaymentStatus(user.status) === PAYMENT_STATUS.Pause_Subscription
    ) {
      onGetUpgradeSubscription({ productItemId: product?.id as string })
        .then((res: UpgradeSubscription) => {
          const detail = res?.data;
          setPlanDetail(detail);
          setPaymentLoading(false);
          setCurrentStep(PaymentSteps.BILLING_PAYMENT);
        })
        .catch(() => {
          setPaymentLoading(false);
        });
    } else {
      onCreateSubscriptionURL(product?.id as string)
        .then((res: CreateSunscriptionUrl) => {
          setPaymentLoading(false);
          window.open(res.data, "_self");
        })
        .catch(() => {
          setPaymentLoading(false);
        });
    }
  }, [product, selectedProduct]);

  const onUpgradePlan = useCallback(async () => {
    setUpdatePlanLoading(true);
    onUpgradeSubscription()
      .then(() => {
        updateUserStatus?.(2);
        authService
          .get()
          .then(() => {
            setUpdatePlanLoading(false);
            push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
          })
          .catch(() => {
            setUpdatePlanLoading(false);
          });
      })
      .catch(() => {
        setUpdatePlanLoading(false);
      });
  }, []);

  const onBack = () => {
    if (currentStep === PaymentSteps.SELECT_PLAN) {
      push(`/${RoutePaths.Settings}/${RoutePaths.PlanAndBilling}`);
    } else {
      setCurrentStep(PaymentSteps.SELECT_PLAN);
    }
  };

  return (
    <MainPageWithScroll headTitle={<HeadTitle titles={[{ id: "payment.tabTitle" }]} />}>
      <PaymentNav steps={Object.values(PaymentSteps)} currentStep={currentStep} />
      <Content className={styles.pageContainer}>
        <MainView>
          {currentStep === PaymentSteps.SELECT_PLAN && (
            <SelectPlanStep
              product={product}
              setProduct={setProduct}
              selectedProduct={selectedProduct}
              paymentLoading={paymentLoading}
              productOptions={productOptions}
              packagesMap={packagesMap}
              onSelectPlan={onSelectPlan}
            />
          )}
          {currentStep === PaymentSteps.BILLING_PAYMENT && (
            <BillingPaymentStep
              productPrice={Number(product?.price)}
              selectedProductPrice={selectedProduct?.price as number}
              planDetail={planDetail}
            />
          )}
        </MainView>
        <ButtonRows top="40" background="transparent">
          <BigButton secondary white onClick={onBack}>
            <FormattedMessage id="form.button.back" />
          </BigButton>
          {currentStep === PaymentSteps.BILLING_PAYMENT && (
            <BigButton isLoading={updatePlanLoading} onClick={onUpgradePlan}>
              <FormattedMessage id="plan.update.btn" />
            </BigButton>
          )}
        </ButtonRows>
      </Content>
    </MainPageWithScroll>
  );
};

export default PaymentPage;
