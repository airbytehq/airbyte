import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { LoadingButton, Button } from "components";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";

import { Mailto } from "./Mailto";

interface IProps {
  price?: string;
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

const CustomPricing = styled.div`
  font-style: normal;
  font-weight: 600;
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
  const { formatMessage } = useIntl();

  return (
    <Container>
      <PricingContainer>
        {price === "custom" ? (
          <CustomPricing>
            <FormattedMessage id="feature.cell.professional.custom.pricing" />
          </CustomPricing>
        ) : (
          <>
            <Price>${price}</Price>&nbsp;
            <PerMonthText>
              /<FormattedMessage id="feature.cell.professional.perMonth" />
            </PerMonthText>
          </>
        )}
      </PricingContainer>
      <Separator />
      <Message>
        <FormattedMessage id="feature.cell.professional.message" />
      </Message>
      <Separator />
      {price === "custom" ? (
        <Mailto
          email={formatMessage({ id: "daspire.support.mail" })}
          subject={formatMessage({ id: "feature.cell.professional.contact.sales.btn" })}
          body={formatMessage({ id: "feature.cell.professional.mailBody" })}
        >
          <Button full size="lg">
            <FormattedMessage id="feature.cell.professional.contact.sales.btn" />
          </Button>
        </Mailto>
      ) : (
        <LoadingButton
          full
          size="lg"
          onClick={onSelectPlan}
          disabled={
            ((Number(price) > 0 ? false : true) || selectPlanBtnDisability) &&
            getPaymentStatus(user.status) !== PAYMENT_STATUS.Pause_Subscription
          }
          isLoading={paymentLoading}
        >
          <FormattedMessage id="feature.cell.professional.select.btn" />
        </LoadingButton>
      )}
    </Container>
  );
};

export default ProfessionalCell;
