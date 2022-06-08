import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H3, Button } from "components/base";

import FeedbackButton from "./FeedbackButton";

const Body = styled.div`
  color: ${({ theme }) => theme.textColor};
  padding: 22px 48px 23px 46px;
  background: ${({ theme }) => theme.beigeColor};
  max-width: 492px;
  border-radius: 0 0 10px 10px;
  text-align: center;
`;

const FeedbackButtons = styled.div`
  padding: 15px 0 29px;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
`;

interface ModalBodyProps {
  onClose: () => void;
  onPassFeedback: (feedback: string) => void;
}

const ModalBody: React.FC<ModalBodyProps> = ({ onClose, onPassFeedback }) => {
  return (
    <Body>
      <H3 center bold parentColor>
        <FormattedMessage id="onboarding.checkData" />
      </H3>
      <FeedbackButtons>
        <FeedbackButton isBad onClick={() => onPassFeedback("dislike")} />
        <FeedbackButton onClick={() => onPassFeedback("like")} />
      </FeedbackButtons>
      <Button secondary onClick={onClose}>
        <FormattedMessage id="onboarding.skipFeedback" />
      </Button>
    </Body>
  );
};

export default ModalBody;
