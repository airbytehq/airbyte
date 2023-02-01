import { Dialog } from "@headlessui/react";
import classNames from "classnames";
import React, { useState } from "react";

import styles from "./Modal.module.scss";
import { Card } from "../Card";
import { Overlay } from "../Overlay";

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

export const Modal: React.FC<React.PropsWithChildren<ModalProps>> = ({
  children,
  title,
  size,
  onClose,
  cardless,
  testId,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const onModalClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  return (
    <Dialog open={isOpen} onClose={onModalClose} data-testid={testId} className={styles.modalPageContainer}>
      <Overlay />
      <div className={styles.modalContainer}>
        <Dialog.Panel className={styles.modalPanel}>
          {cardless ? (
            children
          ) : (
            <Card title={title} className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
              {children}
            </Card>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
