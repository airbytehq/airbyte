import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  Description,
  Dialog,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";
import React from "react";
import styles from "./Modal.module.css";

export const Overlay = () => (
  <div className={styles.modalOverlay} aria-hidden="true" />
);

const CloseButton = ({ onClose }) => {
  return (
    <button onClick={onClose} className={styles.modalCloseButton}>
      <FontAwesomeIcon icon={faXmark} />
    </button>
  );
};

export const Modal = ({ title, isOpen, description, onClose, children }) => {
  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      className={styles.modalPageContainer}
    >
      <Overlay />
      <div className={styles.modalContainer}>
        <DialogPanel className={styles.modalPanel}>
          <div className={styles.modalHeader}>

          <DialogTitle className={styles.modalTitle}>{title}
            
          </DialogTitle>
          <CloseButton onClose={onClose} />
          </div>
          <Description>{description}</Description>
          {children}
        </DialogPanel>
      </div>
    </Dialog>
  );
};
