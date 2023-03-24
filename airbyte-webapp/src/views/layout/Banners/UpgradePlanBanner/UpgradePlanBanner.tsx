import React, { useState, useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
// import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useAuthDetail } from "services/auth/AuthSpecificationService";
import { useUserPlanDetail } from "services/payments/PaymentsService";

import styles from "../banners.module.scss";
import { UnauthorizedModal } from "./components/UnauthorizedModal";

interface IProps {
  onBillingPage: () => void;
}

const Banner = styled.div`
  width: calc(100% - 248px);
  position: fixed;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const Text = styled.div`
  font-weight: 500;
  font-size: 13px;
  line-height: 24px;
  display: flex;
  align-items: center;
  color: #ffffff;
  margin-right: 50px;
`;

export const UpgradePlanBanner: React.FC<IProps> = ({ onBillingPage }) => {
  const { user, updateUserStatus } = useUser();
  const { pathname } = useRouter();
  const userPlanDetail = useUserPlanDetail();
  const { status } = useAuthDetail();
  const { expiresTime } = userPlanDetail;

  useEffect(() => {
    if (status && user.status !== status) {
      updateUserStatus?.(status);
    }
  }, [status, updateUserStatus, user.status]);

  const remainingDaysForFreeTrial = (): number => {
    const currentDate: Date = new Date();
    const expiryDate: Date = new Date(expiresTime * 1000);
    const diff = expiryDate.getTime() - currentDate.getTime();
    const diffDays = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const isUpgradePlanBanner = (): boolean => {
    let showUpgradePlanBanner = false;
    if (getPaymentStatus(user.status) === PAYMENT_STATUS.Free_Trial) {
      if (!pathname.split("/").includes(RoutePaths.Payment)) {
        showUpgradePlanBanner = true;
      }
    }
    return showUpgradePlanBanner;
  };

  const [isAuthorized, setIsAuthorized] = useState<boolean>(false);

  const onUpgradePlan = () => {
    if (
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator_Owner ||
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator
    ) {
      onBillingPage();
    } else {
      setIsAuthorized(true);
    }
  };

  if (isUpgradePlanBanner()) {
    return (
      <>
        <Banner className={styles.banner}>
          <Text>
            <FormattedMessage
              id={
                remainingDaysForFreeTrial() >= 0 ? "upgrade.plan.trialPeriod.countdown" : "upgrade.plan.trialPeriod.end"
              }
              values={{ count: remainingDaysForFreeTrial() }}
            />
          </Text>
          <Button size="m" black onClick={() => onUpgradePlan()}>
            <FormattedMessage id="upgrade.plan.btn" />
          </Button>
        </Banner>
        {isAuthorized && <UnauthorizedModal onClose={() => setIsAuthorized(false)} />}
        {/* <Separator height="40px" /> */}
      </>
    );
  }
  return null;
};
