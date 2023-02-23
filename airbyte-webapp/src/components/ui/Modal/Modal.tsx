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
  /**
   * If specified, the full content of the modal including header, body and footer is wrapped in this component (only a class name prop might be set on the component)
   */
  wrapIn?: React.FC<React.PropsWithChildren<{ className?: string }>>;
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
  wrapIn,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const onModalClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  const Wrapper = wrapIn || "div";

  return (
    <Dialog open={isOpen} onClose={onModalClose} data-testid={testId} className={styles.modalPageContainer}>
      <Overlay />
      <Wrapper className={styles.modalContainer}>
        <Dialog.Panel className={styles.modalPanel}>
          {cardless ? (
            children
          ) : (
            <Card title={title} className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}>
              {children}
            </Card>
          )}
        </Dialog.Panel>
      </Wrapper>
    </Dialog>
  );
};
