import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, ModalBody, Button } from "components";

interface IProps {
  onClose?: () => void;
}

const ModalBodyContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
`;

const UnauthorizedText = styled.div`
  font-weight: 400;
  font-size: 16px;
  line-height: 30px;
  color: #27272a;
  margin-bottom: 50px;
`;

export const UnauthorizedModal: React.FC<IProps> = ({ onClose }) => {
  return (
    <Modal size="md" onClose={onClose}>
      <ModalBody>
        <ModalBodyContainer>
          <UnauthorizedText>
            <FormattedMessage id="unauthorized.modal.text1" />
            <br />
            <FormattedMessage id="unauthorized.modal.text2" />
          </UnauthorizedText>
          <Button size="lg" onClick={onClose}>
            <FormattedMessage id="unauthorized.modal.btn" />
          </Button>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};
