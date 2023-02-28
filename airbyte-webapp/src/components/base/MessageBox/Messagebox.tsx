import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { CrossIcon } from "components/icons/CrossIcon";

interface IProps {
  message?: string;
  onClose?: () => void;
}

const Container = styled.div`
  min-width: 600px;
  background: #eff6ff;
  border-radius: 6px;
  top: 22px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  position: absolute;
  z-index: 3;
  left: 50%;
  transform: translateX(-50%);
  min-width: 750px;
`;

const Message = styled.div`
  font-weight: 400;
  font-size: 14px;
  line-height: 20px;
  color: #1e40af;
  padding: 17px;
`;

const CrossButton = styled.button`
  margin-right: 17px;
  cursor: pointer;
  padding: 0;
  border: none;
  background-color: transparent;
  color: #1e40af;
`;

export const MessageBox: React.FC<IProps> = ({ message, onClose }) => {
  useEffect(() => {
    const intervalID = setTimeout(() => onClose?.(), 3000);

    return () => clearInterval(intervalID);
  }, [message]);

  if (!message) {
    return null;
  }

  return (
    <Container>
      <Message>
        <FormattedMessage id={message} />
      </Message>
      <CrossButton onClick={onClose}>
        <CrossIcon />
      </CrossButton>
    </Container>
  );
};
