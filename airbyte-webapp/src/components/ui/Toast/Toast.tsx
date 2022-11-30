import { faCheck, faExclamation, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import { Button } from "../Button";
// eslint-disable-next-line css-modules/no-unused-class
import styles from "./Toast.module.scss";

export enum ToastType {
  WARNING = "warning",
  SUCCESS = "success",
  ERROR = "error",
  INFO = "info",
}

interface ToastProps {
  title: string | React.ReactNode;
  text?: string | React.ReactNode;
  type?: ToastType;
  hasError?: boolean;
  onAction?: () => void;
  onClose?: () => void;
}

const ICON_MAPPING = {
  [ToastType.WARNING]: faExclamation,
  [ToastType.ERROR]: faTimes,
  [ToastType.SUCCESS]: faCheck,
  [ToastType.INFO]: faExclamation,
};

export const Toast: React.FC<ToastProps> = ({ type = ToastType.INFO, onAction, onClose, title, text }) => {
  return (
    <div className={classNames(styles.toastContainer, styles[type])}>
      <div className={classNames(styles.iconContainer)}>
        <FontAwesomeIcon icon={ICON_MAPPING[type]} className={styles.toastIcon} />
      </div>
      <div>
        <h5 className={styles.title}>{title}</h5>
        {text && <div className={styles.text}>{text}</div>}
      </div>
      {onAction && (
        <Button className={styles.actionButton} onClick={onAction}>
          Action
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
