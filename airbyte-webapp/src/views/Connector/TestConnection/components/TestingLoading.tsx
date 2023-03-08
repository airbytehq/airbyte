import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";

const Text = styled.div`
  font-size: 28px;
  line-height: 40px;
  margin-bottom: 120px;
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
