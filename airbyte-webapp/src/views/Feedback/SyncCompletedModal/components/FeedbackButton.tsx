import React from "react";
import styled from "styled-components";

import BadIcon from "./BadIcon";
import GoodIcon from "./GoodIcon";

interface FeedbackButtonProps {
  isBad?: boolean;
  onClick: () => void;
}

const ButtonView = styled.div<FeedbackButtonProps>`
  color: ${({ theme, isBad }) => (isBad ? theme.redColor : theme.primaryColor)};
  height: 133px;
  width: 133px;
  background: ${({ theme }) => theme.whiteColor};
  margin: 0 10px;
  box-shadow: 0 19px 15px -15px #d1d1db;
  border-radius: 24px;
  cursor: pointer;
  text-align: center;
  padding-top: ${({ isBad }) => (isBad ? 40 : 32)}px;
`;

const FeedbackButton: React.FC<FeedbackButtonProps> = ({ isBad, onClick }) => {
  return (
    <ButtonView isBad={isBad} onClick={onClick}>
      {isBad ? <BadIcon /> : <GoodIcon />}
    </ButtonView>
  );
};

export default FeedbackButton;
