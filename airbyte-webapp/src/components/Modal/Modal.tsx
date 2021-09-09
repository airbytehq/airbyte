import React, { useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import styled, { keyframes } from "styled-components";

import ContentCard from "components/ContentCard";

export type IProps = {
  title?: string | React.ReactNode;
  onClose?: () => void;
  clear?: boolean;
  closeOnBackground?: boolean;
};

const fadeIn = keyframes`
  from { opacity: 0; }
`;

const Overlay = styled.div`
  animation: ${fadeIn} 0.2s ease-out;
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 15, 23, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
`;

const Modal: React.FC<IProps> = ({
  children,
  title,
  onClose,
  clear,
  closeOnBackground,
}) => {
  const handleUserKeyPress = useCallback((event, closeModal) => {
    const { keyCode } = event;
    if (keyCode === 27) {
      closeModal();
    }
  }, []);

  useEffect(() => {
    onClose &&
      window.addEventListener("keydown", (event) =>
        handleUserKeyPress(event, onClose)
      );

    return () => {
      onClose &&
        window.removeEventListener("keydown", (event) =>
          handleUserKeyPress(event, onClose)
        );
    };
  }, [handleUserKeyPress, onClose]);

  return createPortal(
    <Overlay onClick={() => (closeOnBackground && onClose ? onClose() : null)}>
      {clear ? children : <ContentCard title={title}>{children}</ContentCard>}
    </Overlay>,
    document.body
  );
};

export default Modal;
