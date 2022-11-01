import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { StatusIcon } from "components/ui/StatusIcon";

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

const ErrorSection: React.FC<{
  errorTitle: React.ReactNode;
  errorMessage: React.ReactNode;
}> = ({ errorMessage, errorTitle }) => (
  <ErrorBlock>
    <Error />
    <div>
      {errorTitle}
      <ErrorText>{errorMessage}</ErrorText>
    </div>
  </ErrorBlock>
);

const TestingConnectionError: React.FC<{ errorMessage: React.ReactNode }> = ({ errorMessage }) => (
  <ErrorSection errorTitle={<FormattedMessage id="form.failedTests" />} errorMessage={errorMessage} />
);

const FetchingConnectorError: React.FC = () => (
  <ErrorSection
    errorTitle={<FormattedMessage id="form.failedFetchingConnector" />}
    errorMessage={<FormattedMessage id="form.tryAgain" />}
  />
);

export { TestingConnectionError, FetchingConnectorError };
