import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { useUserPlanDetail } from "services/payments/PaymentsService";

interface IProps {
  onUpgradePlan?: () => void;
}

const Container = styled.div`
  width: 100%;
  height: 90px;
  background-color: #9596a4;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const Text = styled.div`
  font-weight: 500;
  font-size: 16px;
  line-height: 24px;
  display: flex;
  align-items: center;
  color: #ffffff;
  margin-right: 50px;
`;

export const UpgradePlanBar: React.FC<IProps> = ({ onUpgradePlan }) => {
  const userPlanDetail = useUserPlanDetail();
  const { expiresTime } = userPlanDetail;

  const remainingDaysForFreeTrial = (): number => {
    const currentDate: any = new Date();
    const expiryDate: any = new Date(expiresTime * 1000);
    const diff = expiryDate - currentDate;
    const diffDays = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return diffDays;
  };
  return (
    <Container>
      <Text>
        <FormattedMessage
          id={remainingDaysForFreeTrial() >= 0 ? "upgrade.plan.trialPeriod.countdown" : "upgrade.plan.trialPeriod.end"}
          values={{ count: remainingDaysForFreeTrial() }}
        />
      </Text>
      <Button size="lg" black onClick={() => onUpgradePlan?.()}>
        <FormattedMessage id="upgrade.plan.btn" />
      </Button>
    </Container>
  );
};
