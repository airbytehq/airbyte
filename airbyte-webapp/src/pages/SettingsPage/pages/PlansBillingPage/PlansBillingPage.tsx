import _ from "lodash";
import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage, FormattedDate } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { ConfirmationModal } from "components/ConfirmationModal";
import { CalendarIcon } from "components/icons/CalendarIcon";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import { PlanItem, PlanItemTypeEnum } from "core/domain/payment";
import { useAppNotification } from "hooks/services/AppNotification";
import { usePrevious } from "hooks/usePrevstate";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";
import { useUserPlanDetail, useAsyncAction } from "services/payments/PaymentsService";

import { IAuthUser } from "../../../../core/AuthContext/authenticatedUser";
import { useHealth } from "../../../../hooks/services/Health";
import { SettingsRoute } from "../../SettingsPage";
import { PlanClause } from "./components/PlanClause";
import styles from "./style.module.scss";

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

const PlansBillingPage: React.FC = () => {
  const { setNotification } = useAppNotification();
  const { push } = useRouter();
  const { user, updateUserStatus, setUser } = useUser();
  const { onPauseSubscription } = useAsyncAction();
  const authService = useAuthenticationService();
  const { healthData } = useHealth();
  const { isUpdatePaymentMethod } = healthData;
  const userPlanDetail = useUserPlanDetail();
  const prevUserPlanDetail = usePrevious(userPlanDetail);

  useEffect(() => {
    if (prevUserPlanDetail?.selectedProduct !== undefined) {
      if (!_.isEqual(userPlanDetail.selectedProduct, prevUserPlanDetail?.selectedProduct)) {
        setNotification({ message: "subscription.plan.update", type: "info" });
      }
    }
  }, [prevUserPlanDetail, userPlanDetail]);

  useEffect(() => {
    if (!user.workspaceId) {
      reAuthenticateUser(user.token as string);
    }
  }, [user.workspaceId]);

  const reAuthenticateUser = useCallback(async (token: string) => {
    authService
      .reAuthenticateUser(token)
      .then((res: IAuthUser) => {
        setUser?.(res);
        push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
      })
      .catch((err: Error) => {
        setNotification({ message: err.message, type: "error" });
      });
  }, []);

  const [toggleCancel, setToggleCancel] = useState<boolean>(false);
  const [confirmLoading, setConfirmLoading] = useState<boolean>(false);

  const toggleCancleSubscriptionModal = () => setToggleCancel(!toggleCancel);

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
            setNotification({ message: "subscription.cancel.successfull", type: "info" });
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

  const onFailedPaymentPage = () => push(`/${RoutePaths.FailedPayment}`);

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
        <ConfirmationModal
          title="subscription.cancelSubscriptionModal.title"
          text="subscription.cancelSubscriptionModal.content"
          submitButtonText="cancelSubscription.modal.btn.confirm"
          cancelButtonText="cancelSubscription.modal.btn.notNow"
          onSubmit={onCancelSubscription}
          onClose={toggleCancleSubscriptionModal}
          loading={confirmLoading}
          contentValues={{
            expiryDate: (
              <FormattedDate
                value={(userPlanDetail.expiresTime as number) * 1000}
                day="numeric"
                month="long"
                year="numeric"
              />
            ),
          }}
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
                  <PlanClause planItem={item} clause={manipulatePlanDetail(item)} key={item.planItemid} />
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className={styles.footer}>
          {getPaymentStatus(user.status) === PAYMENT_STATUS.Subscription && (
            <CancelSubscriptionBtn size="xl" onClick={toggleCancleSubscriptionModal}>
              <BtnText color="#6B6B6F">
                <FormattedMessage id="plan.cancel.btn" />
              </BtnText>
            </CancelSubscriptionBtn>
          )}
          <ButtonSeparator />
          {isUpdatePaymentMethod ? (
            <Button size="xl" onClick={onFailedPaymentPage}>
              <BtnText>
                <FormattedMessage id="update.payment.button" />
              </BtnText>
            </Button>
          ) : (
            <Button size="xl" onClick={upgradePlan}>
              <BtnText>
                <FormattedMessage id="plan.upgrade.btn" />
              </BtnText>
            </Button>
          )}
        </div>
      </div>
    </>
  );
};

export default PlansBillingPage;
