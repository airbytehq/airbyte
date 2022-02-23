import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Spinner from "components/Spinner";

const SpinnerBlock = styled.div`
  padding: 40px;
  text-align: center;
`;

const FetchMessage = styled.div`
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.textColor};
  margin-top: 15px;
  white-space: pre-line;
`;

const LoadingSchema: React.FC = () => (
  <SpinnerBlock>
    <Spinner />
    <FetchMessage>
      <FormattedMessage id="onboarding.fetchingSchema" />
    </FetchMessage>
  </SpinnerBlock>
);

export default LoadingSchema;
