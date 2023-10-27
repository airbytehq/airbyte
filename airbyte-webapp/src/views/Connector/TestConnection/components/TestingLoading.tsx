import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";

const Text = styled.div`
  font-size: 28px;
  line-height: 40px;
  margin-bottom: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  @media (max-width: 768px) {
    font-size: 18px;
    line-height: 30px;
  }
`;

const Loading = keyframes`
0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
`;

const LoadingImage = styled.img`
  width: 100px;
  height: 100px;
  display: inline-block;
  animation: ${Loading} 1.8s linear infinite;
  @media (max-width: 768px) {
    width: 50px;
    height: 50px;
  }
`;

const TestingLoading: React.FC = () => {
  return (
    <>
      <Text>
        <FormattedMessage id="form.testing" />
      </Text>
      <LoadingImage src="/icons/loading-icon.png" alt="loading-icon" />
    </>
  );
};

export default TestingLoading;
