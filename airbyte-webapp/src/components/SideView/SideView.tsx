import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

import { Actions, Container, Content, Body, Close, Header } from "./styled";

type Props = {
  headerLink?: React.ReactNode | string;
  onClose: () => void;
};

const SideView: React.FC<Props> = ({ children, onClose, headerLink }) => {
  useEffect(() => {
    const handleEsq = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keyup", handleEsq);
    return () => document.removeEventListener("keyup", handleEsq);
  });

  return createPortal(
    <Container>
      <Content>
        <Header>
          <Actions>{headerLink}</Actions>
          <Close onClick={onClose} icon={faTimes} />
        </Header>
        <Body>{children}</Body>
      </Content>
    </Container>,
    document.body
  );
};

export default SideView;
