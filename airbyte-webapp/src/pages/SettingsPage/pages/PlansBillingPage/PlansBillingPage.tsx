import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { CalendarIcon } from "components/icons/CalendarIcon";
import { Separator } from "components/Separator";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

import { CancelPlanModal } from "./components/CancelPlanModal";
import PlanClause from "./components/PlanClause";
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

const PlansBillingPage: React.FC = () => {
  const { push } = useRouter();

  const [toggleCancel, setToggleCancel] = useState<boolean>(false);

  const cancelPlan = () => setToggleCancel(!toggleCancel);
  const upgradePlan = () => push(`/${RoutePaths.Payment}`);

  return (
    <>
      {toggleCancel && <CancelPlanModal onClose={cancelPlan} />}
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
            <div className={styles.planValue}>Free trial</div>
          </div>
          <Separator height="40px" />
          <div className={styles.rowContainer}>
            <div className={styles.planTitle}>
              <FormattedMessage id="plan.endsOn.heading" />
            </div>
            <div className={styles.planValue}>4 Nov 2022</div>
          </div>
          <Separator height="40px" />
          <div className={styles.planDetailContainer}>
            <div className={styles.planTitle}>
              <FormattedMessage id="plan.details.heading" />
            </div>
            <div className={styles.planDetailRowContainer}>
              <div className={styles.rowContainer}>
                <PlanClause text="Unlimited no. of rows" />
                <PlanClause text="50 connections" />
              </div>
              <Separator height="20px" />
              <div className={styles.rowContainer}>
                <PlanClause text="Unlimited users" />
                <PlanClause text="5 concurrent jobs" />
              </div>
              <Separator height="20px" />
              <div className={styles.rowContainer}>
                <PlanClause text="Unlimited data sources" />
                <PlanClause text="Replication frequency: 5 mins - 24 hours" />
              </div>
              <Separator height="20px" />
              <div className={styles.rowContainer}>
                <PlanClause text="Unlimited destinations" />
                <PlanClause text="Supported replication type: full" />
              </div>
              <Separator height="20px" />
              <div className={styles.rowContainer}>
                <PlanClause text="Standard email support" />
              </div>
            </div>
          </div>
        </div>
        <div className={styles.footer}>
          <CancelSubscriptionBtn size="xl" onClick={cancelPlan}>
            <BtnText color="#6B6B6F">
              <FormattedMessage id="plan.cancel.btn" />
            </BtnText>
          </CancelSubscriptionBtn>
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
