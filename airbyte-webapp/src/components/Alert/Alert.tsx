import React from "react";
import styled from "styled-components";

import { CrossIcon } from "components/icons/CrossIcon";

interface IProps {
  message?: string;
  formattedMessage?: React.ReactNode;
  onClose: () => void;
}

export const AlertContainer = styled.div`
  width: 100%;
  max-width: 900px;
  height: 52px;
  border-radius: 6px;
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 99;
  background-color: #fef2f2;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0px 20px;
`;

export const Message = styled.div`
  width: 100%;
  font-weight: 400;
  font-size: 14px;
  line-height: 20px;
  color: #991b1b;
`;

export const CrossButton = styled.button`
  cursor: pointer;
  border: none;
  background-color: transparent;
`;

const Alert: React.FC<IProps> = ({ message, onClose, formattedMessage }) => {
  if (message || formattedMessage) {
    return (
      <AlertContainer>
        <Message>{formattedMessage ? formattedMessage : message}</Message>
        <CrossButton onClick={onClose}>
          <CrossIcon color="#F87171" />
        </CrossButton>
      </AlertContainer>
    );
  }
  return null;
};

export default Alert;
