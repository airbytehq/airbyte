import { forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { createPortal } from "react-dom";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

import { Container, Content, Body, Close, Header } from "./styled";

type Props = {
  onClose?: () => void;
  onOpen?: () => void;
  children?: string | React.ReactNode;
};

export type SideViewRef = {
  close: () => void;
  open: () => void;
};

const SideView = forwardRef<SideViewRef, Props>(
  ({ children, onOpen, onClose }, ref) => {
    const [isOpen, setIsOpen] = useState<boolean>(false);

    const handleClose = () => {
      setIsOpen(false);

      if (onClose) {
        onClose();
      }
    };

    const handleOpen = () => {
      setIsOpen(true);

      if (onOpen) {
        onOpen();
      }
    };

    useImperativeHandle<SideViewRef, SideViewRef>(ref, () => ({
      close: handleClose,
      open: handleOpen,
    }));

    useEffect(() => {
      const handleEsq = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
          handleClose();
        }
      };

      document.addEventListener("keyup", handleEsq);
      return () => document.removeEventListener("keyup", handleEsq);
    });

    return isOpen
      ? createPortal(
          <Container>
            <Content>
              <Header>
                <Close onClick={handleClose} icon={faTimes} />
              </Header>
              <Body>{children}</Body>
            </Content>
          </Container>,
          document.body
        )
      : null;
  }
);

export default SideView;
