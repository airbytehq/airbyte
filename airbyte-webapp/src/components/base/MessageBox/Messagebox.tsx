import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { CrossIcon } from "components/icons/CrossIcon";

interface IProps {
  message?: string;
  onClose?: () => void;
  type: "info" | "error";
  position?: "left" | "center" | "right";
}

const Container = styled.div<{ type: "info" | "error" }>`
  min-width: 600px;
  background: ${({ type }) => (type === "error" ? "#FEF2F2" : "#eff6ff")};
  border-radius: 6px;
  top: 22px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  position: fixed;
  z-index: 1001;
  left: 50%;
  transform: translateX(-50%);
  min-width: 750px;
  z-index: 10003;
`;

const Message = styled.div<{ type: "info" | "error"; position?: "left" | "center" | "right" }>`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: ${({ type }) => (type === "error" ? "#991B1B" : "#1e40af")};
  padding: 17px;
  width: 100%;
  text-align: ${({ position }) => (position ? position : "left")};
`;

const CrossButton = styled.button`
  margin-right: 17px;
  cursor: pointer;
  padding: 0;
  border: none;
  background-color: transparent;
  color: #1e40af;
`;

export const MessageBox: React.FC<IProps> = ({ message, onClose, type, position }) => {
  useEffect(() => {
    const intervalID = setTimeout(() => onClose?.(), 3000);

    return () => clearInterval(intervalID);
  }, [message]);

  if (!message) {
    return null;
  }

  return (
    <Container type={type}>
      <Message type={type} position={position}>
        <FormattedMessage id={message} />
      </Message>
      <CrossButton onClick={onClose}>
        <CrossIcon color={type === "error" ? "#991B1B" : "currentColor"} />
      </CrossButton>
    </Container>
  );
};
