import classNames from "classnames";
import React, { useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

import ContentCard from "components/ContentCard";

import styles from "./Modal.module.scss";

export interface ModalProps {
  title?: string | React.ReactNode;
  onClose?: () => void;
  clear?: boolean;
  closeOnBackground?: boolean;
  size?: "sm" | "md" | "lg" | "xl";
  testId?: string;
}

const cardStyleBySize = {
  sm: styles.sm,
  md: styles.md,
  lg: styles.lg,
  xl: styles.xl,
};

const Modal: React.FC<ModalProps> = ({ children, title, onClose, clear, closeOnBackground, size, testId }) => {
  const handleUserKeyPress = useCallback((event: KeyboardEvent, closeModal: () => void) => {
    const { key } = event;
    // Escape key
    if (key === "Escape") {
      closeModal();
    }
  }, []);

  useEffect(() => {
    if (!onClose) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => handleUserKeyPress(event, onClose);
    window.addEventListener("keydown", onKeyDown);

    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [handleUserKeyPress, onClose]);

  return createPortal(
    <div
      className={styles.modal}
      onClick={() => (closeOnBackground && onClose ? onClose() : null)}
      data-testid={testId}
    >
      {clear ? (
        children
      ) : (
        <ContentCard title={title} className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
          {children}
        </ContentCard>
      )}
    </div>,
    document.body
  );
};

export default Modal;
