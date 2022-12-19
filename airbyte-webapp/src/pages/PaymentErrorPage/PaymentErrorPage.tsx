import React from "react";
import styled from "styled-components";

const Container = styled.div`
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 28px;
`;

const PaymentErrorPage: React.FC = () => {
  return <Container>Something went wrong in payment</Container>;
};

export default PaymentErrorPage;
