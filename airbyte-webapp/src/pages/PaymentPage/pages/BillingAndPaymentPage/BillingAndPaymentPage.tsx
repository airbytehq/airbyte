import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Container = styled.div``;

const BillingAndPaymentPage: React.FC = () => {
  return (
    <Container>
      <FormattedMessage id="plan.billing.payment" />
    </Container>
  );
};

export default BillingAndPaymentPage;
