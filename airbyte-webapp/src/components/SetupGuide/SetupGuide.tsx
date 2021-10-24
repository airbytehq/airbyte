import { forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import styled, { keyframes } from "styled-components";
import { createPortal } from "react-dom";
import ReactMarkdown from "react-markdown";
import remark from "remark-gfm";

interface Props {
  content?: string;
  shouldBeShown?: boolean;
  onClose?: () => void;
  onOpen?: () => void;
}

export interface SetupGuideRef {
  close: () => void;
  open: () => void;
}

const Close = styled(FontAwesomeIcon)`
  cursor: pointer;
  font-size: 18px;
`;

const Body = styled.div``;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 60px;
`;

const Container = styled.div`
  display: flex;
  position: absolute;
  z-index: 99999;
  width: 100vw;
  height: 100vh;
  top: 0;
  left: 0;
  justify-content: flex-end;
  background-color: rgba(32, 32, 32, 0.09);
`;

const animation = keyframes`
  from {
    opacity: 0;
		transform: translate3d(100%, 0, 0);
  }

  to {
    opacity: 1;
		transform: none;
  }
`;

const Content = styled.div`
  background-color: #fff;
  height: 100vh;
  width: 60vw;
  top: 0;
  right: 0;
  box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
    0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);
  padding: 20px 50px;
  overflow: scroll;
  animation-name: ${animation};
  animation-duration: 0.1s;
  animation-fill-mode: both;
`;

const SetupGuide = forwardRef<SetupGuideRef, Props>(
  ({ content, shouldBeShown, onClose, onOpen }, ref) => {
    const [isOpen, setIsOpen] = useState<boolean>(false);

    const handleClose = () => {
      setIsOpen(false);

      if (onClose && typeof onClose === "function") {
        onClose();
      }
    };

    const handleOpen = () => {
      setIsOpen(true);

      if (onOpen && typeof onOpen === "function") {
        onOpen();
      }
    };

    useImperativeHandle<SetupGuideRef, SetupGuideRef>(ref, () => ({
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

    return isOpen && shouldBeShown
      ? createPortal(
          <Container>
            <Content>
              <Header>
                <Close onClick={handleClose} icon={faTimes} />
              </Header>
              <Body>
                <ReactMarkdown
                  remarkPlugins={[remark]}
                  children={content as string}
                />
              </Body>
            </Content>
          </Container>,
          document.body
        )
      : null;
  }
);

export default SetupGuide;
