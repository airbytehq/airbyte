import React, { useState, useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { useUser } from "core/AuthContext";
import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import { useAuthDetail } from "services/auth/AuthSpecificationService";
import { useUserPlanDetail } from "services/payments/PaymentsService";

import styles from "../banners.module.scss";
import { UnauthorizedModal } from "./components/UnauthorizedModal";

interface IProps {
  onBillingPage: () => void;
}

const Banner = styled.div`
  width: 100%;
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
  const { status } = useAuthDetail();
  const userPlanDetail = useUserPlanDetail();
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
    </>
  );
};
