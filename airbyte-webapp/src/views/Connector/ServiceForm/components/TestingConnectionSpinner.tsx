import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Spinner } from "components";

const LoadingContainer = styled.div`
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Loader = styled.div`
  margin-right: 10px;
`;

const TestingConnectionSpinner: React.FC = () => {
  return (
    <LoadingContainer>
      <Loader>
        <Spinner />
      </Loader>
      <FormattedMessage id="form.testingConnection" />
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
