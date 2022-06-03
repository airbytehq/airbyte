import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useRef } from "react";
import { createPortal } from "react-dom";
import { useClickAway, useKey } from "react-use";

import { Actions, Body, Close, Container, Content, Header } from "./styled";

interface Props {
  headerLink?: React.ReactNode | string;
  onClose: () => void;
}

const EXIT_KEY = "Escape";

const SideView: React.FC<Props> = ({ children, onClose, headerLink }) => {
  const ref = useRef(null);

  useKey(EXIT_KEY, onClose);
  useClickAway(ref, onClose);

  return createPortal(
    <Container>
      <Content ref={ref}>
        <Header>
          <Actions>{headerLink}</Actions>
          <Close onClick={onClose}>
            <FontAwesomeIcon icon={faTimes} size="xs" />
          </Close>
        </Header>
        <Body>{children}</Body>
      </Content>
    </Container>,
    document.body
  );
};

export default SideView;
