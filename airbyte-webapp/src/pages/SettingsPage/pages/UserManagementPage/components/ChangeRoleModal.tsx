import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, ModalBody, LoadingButton, Button } from "components";
import { Separator } from "components/Separator";

interface IProps {
  onClose?: () => void;
  onChangeRole?: () => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

const ModalBodyContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
`;

const ModalHeading = styled.div`
  font-weight: 700;
  font-size: 18px;
  line-height: 22px;
  color: ${({ theme }) => theme.black300};
`;

const ConfirmationMessage = styled.div`
  font-weight: 400;
  font-size: 13px;
  line-height: 22px;
  color: ${({ theme }) => theme.black300};
`;

const ButtonsContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const ChangeBtn = styled(LoadingButton)`
  margin-right: 68px;
`;

const ChangeRoleModal: React.FC<IProps> = ({ onClose, onChangeRole, onCancel, isLoading }) => {
  return (
    <Modal size="sm" onClose={onClose}>
      <ModalBody>
        <ModalBodyContainer>
          <ModalHeading>
            <FormattedMessage id="user.changeRoleModal.heading" />
          </ModalHeading>
          <Separator />
          <ConfirmationMessage>
            <FormattedMessage id="user.changeRoleModal.confirmationMessage" />
          </ConfirmationMessage>
          <Separator height="50px" />
          <ButtonsContainer>
            <ChangeBtn size="lg" secondary onClick={onChangeRole} isLoading={isLoading}>
              <FormattedMessage id="user.changeRoleModal.changeBtn" />
            </ChangeBtn>
            <Button size="lg" onClick={onCancel}>
              <FormattedMessage id="user.changeRoleModal.cancelBtn" />
            </Button>
          </ButtonsContainer>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};

export default ChangeRoleModal;
