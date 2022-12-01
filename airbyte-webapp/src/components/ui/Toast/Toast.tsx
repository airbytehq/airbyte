import { faCheck, faExclamation, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import { Text } from "components/ui/Text";

import { Button } from "../Button";
/* eslint css-modules/no-unused-class: [2, { markAsUsed: ['warning', 'error', 'success', 'info'] }] */
import styles from "./Toast.module.scss";

export enum ToastType {
  WARNING = "warning",
  SUCCESS = "success",
  ERROR = "error",
  INFO = "info",
}

interface ToastProps {
  text?: string | React.ReactNode;
  type?: ToastType;
  hasError?: boolean;
  onAction?: () => void;
  actionBtnText?: string;
  onClose?: () => void;
}

const ICON_MAPPING = {
  [ToastType.WARNING]: faExclamation,
  [ToastType.ERROR]: faTimes,
  [ToastType.SUCCESS]: faCheck,
  [ToastType.INFO]: faExclamation,
};

export const Toast: React.FC<ToastProps> = ({ type = ToastType.INFO, onAction, actionBtnText, onClose, text }) => {
  return (
    <div className={classNames(styles.toastContainer, styles[type])}>
      <div className={classNames(styles.iconContainer)}>
        <FontAwesomeIcon icon={ICON_MAPPING[type]} className={styles.toastIcon} />
      </div>
      <div>
        {text && (
          <Text size="lg" className={styles.text}>
            {text}
          </Text>
        )}
      </div>
      {onAction && (
        <Button className={styles.actionButton} onClick={onAction}>
          {actionBtnText}
        </Button>
      )}
      {onClose && (
        <Button
          className={styles.closeButton}
          variant="clear"
          onClick={onClose}
          icon={<FontAwesomeIcon icon={faTimes} />}
        />
      )}
    </div>
  );
};
