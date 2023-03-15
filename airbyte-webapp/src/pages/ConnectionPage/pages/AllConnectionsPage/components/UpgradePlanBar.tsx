import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
// import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import useRouter from "hooks/useRouter";
import { UnauthorizedModal } from "pages/ConnectionPage/pages/AllConnectionsPage/components/UnauthorizedModal";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";
import { useUserPlanDetail } from "services/payments/PaymentsService";

const Container = styled.div`
  width: 100%;
  height: 40px;
  background-color: #9596a4;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: 1000;
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

export const UpgradePlanBar: React.FC = () => {
  const { user } = useUser();
  const { pathname, push } = useRouter();
  const userPlanDetail = useUserPlanDetail();
  const { expiresTime } = userPlanDetail;

  const remainingDaysForFreeTrial = (): number => {
    const currentDate: any = new Date();
    const expiryDate: any = new Date(expiresTime * 1000);
    const diff = expiryDate - currentDate;
    const diffDays = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const isUpgradePlanBar = (): boolean => {
    let showUpgradePlanBar = false;
    if (getPaymentStatus(user.status) === PAYMENT_STATUS.Free_Trial) {
      if (!pathname.split("/").includes(RoutePaths.Payment)) {
        showUpgradePlanBar = true;
      }
    }
    return showUpgradePlanBar;
  };

  const [isAuthorized, setIsAuthorized] = useState<boolean>(false);

  const onUpgradePlan = () => {
    if (
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator_Owner ||
      getRoleAgainstRoleNumber(user.role) === ROLES.Administrator
    ) {
      push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
    } else {
      setIsAuthorized(true);
    }
  };

  if (isUpgradePlanBar()) {
    return (
      <>
        <Container>
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
        </Container>
        {isAuthorized && <UnauthorizedModal onClose={() => setIsAuthorized(false)} />}
        {/* <Separator height="40px" /> */}
      </>
    );
  }
  return null;
};
