import React from "react";

import Modal from "components/Modal";

import ModalBody from "./components/ModalBody";
import ModalHeader from "./components/ModalHeader";

interface SyncCompletedModalProps {
  onClose: () => void;
  onPassFeedback: (feedback: string) => void;
}

const SyncCompletedModal: React.FC<SyncCompletedModalProps> = ({ onClose, onPassFeedback }) => {
  return (
    <Modal>
      <ModalHeader />
      <ModalBody onClose={onClose} onPassFeedback={onPassFeedback} />
    </Modal>
  );
};

export default SyncCompletedModal;
