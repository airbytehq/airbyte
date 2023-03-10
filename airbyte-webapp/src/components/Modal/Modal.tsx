import { Dialog } from "@headlessui/react";
import classNames from "classnames";
import React, { useState } from "react";

// import { Card } from "../base/Card";
import styles from "./Modal.module.scss";

export interface ModalProps {
  title?: string | React.ReactNode;
  onClose?: () => void;
  cardless?: boolean;
  size?: "sm" | "md" | "lg" | "xl";
  testId?: string;
}

const cardStyleBySize = {
  sm: styles.sm,
  md: styles.md,
  lg: styles.lg,
  xl: styles.xl,
};

const Modal: React.FC<ModalProps> = ({ children, size, title, onClose, cardless, testId }) => {
  //
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
          {cardless ? (
            children
          ) : (
            <div className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
              <div className={styles.cardTitle}>{title}</div>
              {children}
            </div>
            // <Card title={title} className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
            //   {children}
            // </Card>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};

export default Modal;
