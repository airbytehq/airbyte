import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useAsyncAction } from "services/payments/PaymentsService";

import { CreateSunscriptionUrl, failedPaymentDetail, GetFailedPaymentDetail } from "../../core/domain/payment";
import PaymentNav from "./components/PaymentNav";
import { PaymentSteps } from "./PaymentPage";
import styles from "./PaymentPage.module.scss";
import BillingPaymentStep from "./steps/BillingPaymentStep";

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainView = styled.div`
  width: 100%;
`;

const FailedPaymentPage: React.FC = () => {
  const { push } = useRouter();
  const [currentStep, setCurrentStep] = useState<string>(PaymentSteps.SELECT_PLAN);
  const [planDetail, setPlanDetail] = useState<GetFailedPaymentDetail>();
  const { onFailedPaymentDetails, onUpdatePaymentMethodURL } = useAsyncAction();
  const [updatePaymentLoading, setUpdatePaymentLoading] = useState<boolean>(false);
  const [fetchLoading, setFetchLoading] = useState<boolean>(false);

  useEffect(() => {
    setCurrentStep(PaymentSteps.BILLING_PAYMENT);
    failedPaymentDetails();
  }, []);

  const onBack = () => {
    push(`/${RoutePaths.Settings}/${RoutePaths.PlanAndBilling}`);
  };

  const failedPaymentDetails = () => {
    setFetchLoading(true);
    onFailedPaymentDetails()
      .then((res: failedPaymentDetail) => {
        const planDetail = res?.data;
        setPlanDetail(planDetail);
        setFetchLoading(false);
      })
      .catch(() => {
        setFetchLoading(false);
      });
  };

  const onUpdatePaymentMethod = () => {
    setUpdatePaymentLoading(true);
    onUpdatePaymentMethodURL(planDetail?.paymentOrderId as string)
      .then((res: CreateSunscriptionUrl) => {
        setUpdatePaymentLoading(false);
        window.open(res.data, "_self");
      })
      .catch(() => {
        setUpdatePaymentLoading(false);
      });
  };

  return (
    <MainPageWithScroll headTitle={<HeadTitle titles={[{ id: "payment.tabTitle" }]} />}>
      <PaymentNav steps={Object.values(PaymentSteps)} currentStep={currentStep} />
      <Content className={styles.pageContainer}>
        {fetchLoading ? (
          <LoadingPage />
        ) : (
          <>
            <MainView>{planDetail && <BillingPaymentStep planDetail={planDetail} />}</MainView>
            <ButtonRows top="40" background="transparent">
              <BigButton secondary white onClick={onBack}>
                <FormattedMessage id="form.button.back" />
              </BigButton>
              <BigButton isLoading={updatePaymentLoading} onClick={onUpdatePaymentMethod}>
                <FormattedMessage id="plan.update.btn" />
              </BigButton>
            </ButtonRows>
          </>
        )}
      </Content>
    </MainPageWithScroll>
  );
};

export default FailedPaymentPage;
