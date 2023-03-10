import React from "react";
import { FormattedDate, FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

// import { LoadingButton } from "components";
import { Separator } from "components/Separator";

import { GetUpgradeSubscriptionDetail } from "core/domain/payment";
import { convert_M_To_Million } from "pages/SettingsPage/pages/PlansBillingPage/PlansBillingPage";

interface IProps {
  productPrice: number;
  selectedProductPrice: number;
  planDetail?: GetUpgradeSubscriptionDetail;
  // onUpdadePlan: () => void;
  // updatePlanLoading: boolean;
}

const Container = styled.div`
  width: 100%;
  background-color: ${({ theme }) => theme.white};
  border-radius: 16px;
  padding: 40px 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const ContentContainer = styled.div`
  width: 430px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Logo = styled.img`
  width: 50px;
  height: 35px;
`;

const PlanName = styled.div`
  font-weight: 500;
  font-size: 32px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
`;

const ContentItem = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
`;

const ContentHeading = styled.div`
  width: 200px;
  font-weight: 500;
  font-size: 14px;
  line-height: 24px;
  color: ${({ theme }) => theme.black300};
  margin-right: 20px;
`;

const ContentText = styled.div`
  width: 100%;
  font-weight: 400;
  font-size: 14px;
  line-height: 24px;
  color: ${({ theme }) => theme.black300};
`;

// const FooterContainer = styled.div`
//   width: 100%;
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   justify-content: center;
// `;

const BillingPaymentStep: React.FC<IProps> = ({
  productPrice,
  selectedProductPrice,
  planDetail,
  // onUpdadePlan,
  // updatePlanLoading,
}) => {
  const { formatMessage } = useIntl();
  const seperatorHeight = "47px";

  const calculateProductDuePrice = (dueToday: number): string | React.ReactElement => {
    if (productPrice < selectedProductPrice) {
      return `0 ${formatMessage({ id: "payment.paymentToReturn" })}`;
    }
    return `${dueToday}`;
  };

  return (
    <>
      <Container>
        <ContentContainer>
          <Logo src="/daspireLogo.svg" alt="logo" />
          <Separator />
          <PlanName>
            <FormattedMessage id="payment.planName" values={{ planName: planDetail?.planName }} />
          </PlanName>
          <Separator height={seperatorHeight} />
          <ContentItem>
            <ContentHeading>
              <FormattedMessage id="plan.detail.rows" />
            </ContentHeading>
            <ContentText>{convert_M_To_Million(planDetail?.productItemName as string)}</ContentText>
          </ContentItem>
          <Separator height={seperatorHeight} />
          <ContentItem>
            <ContentHeading>
              <FormattedMessage id="plan.detail.billing" />
            </ContentHeading>
            <ContentText>
              US ${planDetail?.productItemPrice}&nbsp;/&nbsp;
              <FormattedMessage id="payment.planDeductionTime" />
            </ContentText>
          </ContentItem>
          <Separator height={seperatorHeight} />
          <ContentItem>
            <ContentHeading>
              <FormattedMessage id="plan.detail.dueToday" />
            </ContentHeading>
            <ContentText>US ${calculateProductDuePrice(planDetail?.totalDueToday as number)}</ContentText>
          </ContentItem>
          <Separator height={seperatorHeight} />
          <ContentItem>
            <ContentHeading>
              <FormattedMessage id="plan.detail.reoccuringBilling" />
            </ContentHeading>
            <ContentText>
              <FormattedMessage id="payment.nextBillingDate" />
              :&nbsp;
              <FormattedDate
                value={(planDetail?.expiresTime as number) * 1000}
                day="numeric"
                month="long"
                year="numeric"
              />
              <br />
              <FormattedMessage id="payment.cancelTime" />
            </ContentText>
          </ContentItem>
        </ContentContainer>
      </Container>
      {/* <Separator height={seperatorHeight} />
      <FooterContainer>
        <LoadingButton size="xl" onClick={onUpdadePlan} isLoading={updatePlanLoading}>
          <FormattedMessage id="plan.update.btn" />
        </LoadingButton>
      </FooterContainer> */}
    </>
  );
};

export default BillingPaymentStep;
