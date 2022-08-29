import { Dialog } from "@headlessui/react";
import classNames from "classnames";
import React, { useState } from "react";

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

export const Modal: React.FC<ModalProps> = ({ children, title, size, onClose, clear, testId }) => {
  const [isOpen, setIsOpen] = useState(true);

  const onModalClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  return (
    <Dialog open={isOpen} onClose={onModalClose} data-testid={testId} className={styles.modalPageContainer}>
      <div className={styles.backdrop} />
      <div className={styles.modalContainer}>
        <Dialog.Panel className={styles.modalPanel}>
          {clear ? (
            children
          ) : (
            <ContentCard title={title} className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
              {children}
            </ContentCard>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
