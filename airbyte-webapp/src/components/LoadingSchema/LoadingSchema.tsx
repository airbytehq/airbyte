import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ProgressBar } from "components/ui/ProgressBar";

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

// Progress Bar runs 4min for discoveries schema
const PROGRESS_BAR_TIME = 60 * 4;

const LoadingSchema: React.FC = () => (
  <SpinnerBlock>
    <ProgressBar runTime={PROGRESS_BAR_TIME} />
    <FetchMessage>
      <FormattedMessage id="onboarding.fetchingSchema" />
    </FetchMessage>
  </SpinnerBlock>
);

export default LoadingSchema;
