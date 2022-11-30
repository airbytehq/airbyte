import React from "react";
import styled from "styled-components";

import { Spinner } from "components/ui/Spinner";

export interface FeedbackBlockProps {
  isLoading?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
}

const SuccessBlock = styled.div`
  margin: -10px 10px;
  color: ${({ theme }) => theme.successColor};
  font-size: 13px;
  line-height: 16px;
  display: inline-block;
  vertical-align: middle;
`;

const ErrorBlock = styled(SuccessBlock)`
  color: ${({ theme }) => theme.dangerColor};
`;

const FeedbackBlock: React.FC<FeedbackBlockProps> = ({ isLoading, errorMessage, successMessage }) => {
  if (isLoading) {
    return (
      <SuccessBlock>
        <Spinner small />
      </SuccessBlock>
    );
  }

  if (errorMessage) {
    return <ErrorBlock>{errorMessage}</ErrorBlock>;
  }

  if (successMessage) {
    return <SuccessBlock>{successMessage}</SuccessBlock>;
  }

  return null;
};

export default FeedbackBlock;
