import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { Actions, Container, Content, Body, Close, Header } from "./styled";

import ClickOutside from "../ClickOutside";

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
      <ClickOutside onClickOut={onClose}>
        <Content>
          <Header>
            <Actions>{headerLink}</Actions>
            <Close onClick={onClose}>
              <FontAwesomeIcon icon={faTimes} size="xs" />
            </Close>
          </Header>
          <Body>{children}</Body>
        </Content>
      </ClickOutside>
    </Container>,
    document.body
  );
};

export default SideView;
