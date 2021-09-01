import React from "react";
// import styled from "styled-components";

import Modal from "components/Modal";
import ModalHeader from "./components/ModalHeader";
import ModalBody from "./components/ModalBody";

// const Content = styled.div`
//   display: flex;
//   flex-direction: row;
// `;

const SyncCompletedModal: React.FC = () => {
  return (
    <Modal>
      <ModalHeader />
      <ModalBody />
    </Modal>
  );
};

export default SyncCompletedModal;
