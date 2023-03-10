import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";

interface IProps {
  price?: number;
  selectPlanBtnDisability: boolean;
  paymentLoading: boolean;
  onSelectPlan?: () => void;
}

const Container = styled.div`
  width: 100%;
  height: auto;
`;

const PricingContainer = styled.div`
  width: 100%;
  display: flex;
`;

const Price = styled.div`
  font-style: normal;
  font-weight: 800;
  font-size: 24px;
  color: ${({ theme }) => theme.black300};
`;

const PerMonthText = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 12px;
  line-height: 24px;
  color: #6b6b6f;
`;

const Message = styled.div`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: #6b6b6f;
`;

const ProfessionalCell: React.FC<IProps> = ({ price = 0, selectPlanBtnDisability, paymentLoading, onSelectPlan }) => {
  const { user } = useUser();
  return (
    <Container>
      <PricingContainer>
        <Price>${price}</Price>&nbsp;
        <PerMonthText>
          /<FormattedMessage id="feature.cell.professional.perMonth" />
        </PerMonthText>
      </PricingContainer>
      <Separator />
      <Message>
        <FormattedMessage id="feature.cell.professional.message" />
      </Message>
      <Separator />
      <LoadingButton
        full
        size="lg"
        onClick={onSelectPlan}
        disabled={
          ((price > 0 ? false : true) || selectPlanBtnDisability) &&
          getPaymentStatus(user.status) !== PAYMENT_STATUS.Pause_Subscription
        }
        isLoading={paymentLoading}
      >
        <FormattedMessage id="feature.cell.professional.btnText" />
      </LoadingButton>
    </Container>
  );
};

export default ProfessionalCell;
