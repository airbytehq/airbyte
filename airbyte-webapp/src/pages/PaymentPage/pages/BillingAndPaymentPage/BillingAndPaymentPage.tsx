import React from "react";
import styled from "styled-components";

import PaymentForm from "./components/PaymentForm";
import PlanCard from "./components/PlanCard";

const Container = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
`;

const BillingAndPaymentPage: React.FC = () => {
  return (
    <Container>
      <PlanCard />
      <PaymentForm />
    </Container>
  );
};

export default BillingAndPaymentPage;
