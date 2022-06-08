import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Spinner from "components/Spinner";

export interface FeedbackProps {
  feedback: string;
}

const Success = styled.div`
  display: inline-block;
  color: ${({ theme }) => theme.successColor};
  font-weight: normal;
  font-size: 13px;
  line-height: 16px;
  margin-left: 5px;
`;

const Loading = styled.div`
  display: inline-block;
  margin: -15px 0 0 5px;
  vertical-align: middle;
  height: 15px;
`;

const Feedback: React.FC<FeedbackProps> = ({ feedback }) => {
  if (feedback === "loading") {
    return (
      <Loading>
        <Spinner small />
      </Loading>
    );
  }
  if (feedback === "success") {
    return (
      <Success>
        <FormattedMessage id="settings.changeSaved" />
      </Success>
    );
  }

  return null;
};

export default Feedback;
