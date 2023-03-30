import React from "react";
import styled from "styled-components";

import FooterButtons from "views/Connector/TestConnection/components/FooterButtons";
import TestingLoading from "views/Connector/TestConnection/components/TestingLoading";
import TestingSuccess from "views/Connector/TestConnection/components/TestingSuccess";

interface Iprops {
  isLoading: boolean;
  type: "destination" | "source";
  onBack: () => void;
  onFinish: () => void;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
`;

const LoadingContainer = styled.div`
  margin: 10% auto 200px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  flex: 1;
`;

const TestConnection: React.FC<Iprops> = ({ isLoading, type, onBack, onFinish }) => {
  return (
    <Container>
      <LoadingContainer>{isLoading ? <TestingLoading /> : <TestingSuccess type={type} />}</LoadingContainer>
      <FooterButtons onBack={onBack} onFinish={onFinish} isLoading={isLoading} />
    </Container>
  );
};

export default TestConnection;
