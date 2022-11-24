import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { CalendarIcon } from "components/icons/CalendarIcon";

import PlanClause from "./components/PlanClause";
import styles from "./style.module.scss";

const Seperator = styled.div<{ height?: number }>`
  width: 100%;
  height: ${({ height }) => (height ? height : 20)}px;
`;

const UpgradePlanBtnText = styled.div`
  font-weight: 500;
  font-size: 14px;
  color: #ffffff;
  padding: 5px;
`;

const PlansBillingPage: React.FC = () => {
  return (
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
        <Seperator height={40} />
        <div className={styles.rowContainer}>
          <div className={styles.planTitle}>
            <FormattedMessage id="plan.endsOn.heading" />
          </div>
          <div className={styles.planValue}>4 Nov 2022</div>
        </div>
        <Seperator height={40} />
        <div className={styles.planDetailContainer}>
          <div className={styles.planTitle}>
            <FormattedMessage id="plan.details.heading" />
          </div>
          <div className={styles.planDetailRowContainer}>
            <div className={styles.rowContainer}>
              <PlanClause text="Unlimited no. of rows" />
              <PlanClause text="50 connections" />
            </div>
            <Seperator height={20} />
            <div className={styles.rowContainer}>
              <PlanClause text="Unlimited users" />
              <PlanClause text="5 concurrent jobs" />
            </div>
            <Seperator height={20} />
            <div className={styles.rowContainer}>
              <PlanClause text="Unlimited data sources" />
              <PlanClause text="Replication frequency: 5 mins - 24 hours" />
            </div>
            <Seperator height={20} />
            <div className={styles.rowContainer}>
              <PlanClause text="Unlimited destinations" />
              <PlanClause text="Supported replication type: full" />
            </div>
            <Seperator height={20} />
            <div className={styles.rowContainer}>
              <PlanClause text="Standard email support" />
            </div>
          </div>
        </div>
      </div>
      <div className={styles.footer}>
        <Button size="xl">
          <UpgradePlanBtnText>
            <FormattedMessage id="plan.upgrade.btn" />
          </UpgradePlanBtnText>
        </Button>
      </div>
    </div>
  );
};

export default PlansBillingPage;
