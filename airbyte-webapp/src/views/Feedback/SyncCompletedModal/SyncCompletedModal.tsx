import React from "react";

import Modal from "components/Modal";
import ModalHeader from "./components/ModalHeader";
import ModalBody from "./components/ModalBody";

type SyncCompletedModalProps = {
  onClose: () => void;
};

const SyncCompletedModal: React.FC<SyncCompletedModalProps> = ({ onClose }) => {
  return (
    <Modal>
      <ModalHeader />
      <ModalBody onClose={onClose} />
    </Modal>
  );
};

export default SyncCompletedModal;
