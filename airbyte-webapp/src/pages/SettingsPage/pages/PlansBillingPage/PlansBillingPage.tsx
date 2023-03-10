import _ from "lodash";
import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage, FormattedDate } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { CalendarIcon } from "components/icons/CalendarIcon";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import { PlanItem, PlanItemTypeEnum } from "core/domain/payment";
import { usePrevious } from "hooks/usePrevstate";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useAuthDetail, useAuthenticationService } from "services/auth/AuthSpecificationService";
import { useUserPlanDetail, useAsyncAction } from "services/payments/PaymentsService";

import { CancelPlanModal } from "./components/CancelPlanModal";
import PlanClause from "./components/PlanClause";
import styles from "./style.module.scss";

interface IProps {
  setMessageId: React.Dispatch<React.SetStateAction<string>>;
  setMessageType: React.Dispatch<React.SetStateAction<"info" | "error">>;
}

const CancelSubscriptionBtn = styled(Button)`
  background-color: ${({ theme }) => theme.white};
  color: #6b6b6f;
  border: 1px solid #d1d5db;
`;

const BtnText = styled.div<{
  color?: string;
}>`
  font-weight: 500;
  font-size: 14px;
  color: ${({ theme, color }) => (color ? color : theme.white)};
  padding: 5px;
`;

const ButtonSeparator = styled.div`
  width: 50px;
`;

export const convert_M_To_Million = (string: string): string | React.ReactElement => {
  if (string.includes("M")) {
    return <FormattedMessage id="payment.amount" values={{ amount: string.substring(0, string.length - 1) }} />;
  }
  return string;
};

const PlansBillingPage: React.FC<IProps> = ({ setMessageId, setMessageType }) => {
  const { push } = useRouter();
  const { user, updateUserStatus } = useUser();
  const { onPauseSubscription } = useAsyncAction();
  const authService = useAuthenticationService();
  const authDetail = useAuthDetail();
  const { status } = authDetail;
  const userPlanDetail = useUserPlanDetail();
  const prevUserPlanDetail = usePrevious(userPlanDetail);

  useEffect(() => {
    if (status && user.status !== status) {
      updateUserStatus?.(status);
    }
  }, [status]);

  useEffect(() => {
    if (prevUserPlanDetail?.selectedProduct !== undefined) {
      if (!_.isEqual(userPlanDetail.selectedProduct, prevUserPlanDetail?.selectedProduct)) {
        setMessageId?.("subscription.plan.update");
        setMessageType("info");
      }
    }
  }, [prevUserPlanDetail, userPlanDetail]);

  const [toggleCancel, setToggleCancel] = useState<boolean>(false);
  const [confirmLoading, setConfirmLoading] = useState<boolean>(false);

  const toggleCancleSuscriptionModal = () => setToggleCancel(!toggleCancel);

  const onCancelSubscription = useCallback(() => {
    setConfirmLoading(true);
    onPauseSubscription()
      .then(() => {
        authService
          .get()
          .then(() => {
            updateUserStatus?.(4);
            setConfirmLoading(false);
            setToggleCancel(false);
            setMessageId?.("subscription.cancel.successfull");
            setMessageType("info");
          })
          .catch(() => {
            setConfirmLoading(false);
          });
      })
      .catch(() => {
        setConfirmLoading(false);
      });
  }, []);

  const upgradePlan = () => push(`/${RoutePaths.Payment}`);

  const manipulatePlanDetail = (planItem: PlanItem): string | React.ReactElement => {
    if (planItem.planItemType === PlanItemTypeEnum.Features) {
      return (
        <>
          {`${planItem.planItemName}: `}
          {convert_M_To_Million(planItem.planItemScopeLang as string)}
        </>
      );
    } else if (planItem.planItemType === PlanItemTypeEnum.Data_Replication) {
      return `${planItem.planItemName}: ${planItem.planItemScopeLang}`;
    } else if (planItem.planItemType === PlanItemTypeEnum.Support) {
      if (planItem.planItemScope === "false") {
        return "";
      }
      return `${planItem.planItemName}: ${planItem.planItemScopeLang}`;
    }
    return "";
  };

  return (
    <>
      {toggleCancel && (
        <CancelPlanModal
          onClose={toggleCancleSuscriptionModal}
          onConfirm={onCancelSubscription}
          onNotNow={toggleCancleSuscriptionModal}
          confirmLoading={confirmLoading}
          expiresOn={userPlanDetail.expiresTime}
        />
      )}
      <div className={styles.container}>
        <div className={styles.header}>
          <CalendarIcon />
          <div className={styles.heading}>
            <FormattedMessage id="settings.plan.heading" />
          </div>
        </div>
        <div className={styles.body}>
          <div className={styles.rowContainer}>
            <div className={styles.planTitle}>
              <FormattedMessage id="plan.type.heading" />
            </div>
            <div className={styles.planValue}>
              {userPlanDetail.name === "Free trial" ? userPlanDetail.name : `${userPlanDetail.name}`}
            </div>
          </div>
          <Separator height="40px" />
          <div className={styles.rowContainer}>
            <div className={styles.planTitle}>
              <FormattedMessage
                id={
                  getPaymentStatus(user.status) === PAYMENT_STATUS.Free_Trial ||
                  getPaymentStatus(user.status) === PAYMENT_STATUS.Pause_Subscription
                    ? "plan.endsOn.heading"
                    : "plan.renewsOn.heading"
                }
              />
            </div>
            <div className={styles.planValue}>
              <FormattedDate value={userPlanDetail.expiresTime * 1000} day="numeric" month="long" year="numeric" />
            </div>
          </div>
          <Separator height="40px" />
          <div className={styles.planDetailContainer}>
            <div className={styles.planTitle}>
              <FormattedMessage id="plan.details.heading" />
            </div>
            <div className={styles.planDetailRowContainer}>
              <div className={styles.rowContainer}>
                {userPlanDetail.planDetail.map((item) => (
                  <PlanClause text={manipulatePlanDetail(item) as string} />
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className={styles.footer}>
          {getPaymentStatus(user.status) === PAYMENT_STATUS.Subscription && (
            <CancelSubscriptionBtn size="xl" onClick={toggleCancleSuscriptionModal}>
              <BtnText color="#6B6B6F">
                <FormattedMessage id="plan.cancel.btn" />
              </BtnText>
            </CancelSubscriptionBtn>
          )}
          <ButtonSeparator />
          <Button size="xl" onClick={upgradePlan}>
            <BtnText>
              <FormattedMessage id="plan.upgrade.btn" />
            </BtnText>
          </Button>
        </div>
      </div>
    </>
  );
};

export default PlansBillingPage;
