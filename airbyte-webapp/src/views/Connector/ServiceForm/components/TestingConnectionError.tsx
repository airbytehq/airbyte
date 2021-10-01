import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import StatusIcon from "components/StatusIcon";

const Error = styled(StatusIcon)`
  padding-left: 1px;
  width: 26px;
  min-width: 26px;
  height: 26px;
  padding-top: 5px;
  font-size: 17px;
`;

const ErrorBlock = styled.div`
  display: flex;
  justify-content: right;
  align-items: center;
  font-weight: 600;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
`;

const ErrorText = styled.div`
  font-weight: normal;
  color: ${({ theme }) => theme.dangerColor};
  max-width: 400px;
`;

const TestingConnectionError: React.FC<{ errorMessage: React.ReactNode }> = ({
  errorMessage,
}) => {
  return (
    <ErrorBlock>
      <Error />
      <div>
        <FormattedMessage id="form.failedTests" />
        <ErrorText>{errorMessage}</ErrorText>
      </div>
    </ErrorBlock>
  );
};

export default TestingConnectionError;
