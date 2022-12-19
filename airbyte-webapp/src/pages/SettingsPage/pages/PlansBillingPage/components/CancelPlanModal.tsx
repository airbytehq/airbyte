import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, ModalBody, LoadingButton } from "components";

interface IProps {
  onClose?: () => void;
  onConfirm?: () => void;
  onNotNow?: () => void;
  confirmLoading?: boolean;
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
  font-size: 20px;
  line-height: 29px;
  color: ${({ theme }) => theme.black300};
  margin-bottom: 35px;
`;

const ModalBodyText = styled.div`
  font-weight: 400;
  font-size: 14px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  margin-bottom: 40px;
`;

const ButtonsContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  padding: 0 40px;
`;

const ConfirmBtn = styled(LoadingButton)`
  background-color: ${({ theme }) => theme.white};
  color: #6b6b6f;
  border: 1px solid #d1d5db;
`;

const BtnText = styled.div<{
  color?: string;
  hide?: boolean;
}>`
  font-weight: 500;
  font-size: 14px;
  color: ${({ theme, color }) => (color ? color : theme.white)};
  opacity: ${({ hide }) => (hide ? 0 : 1)};
`;

export const CancelPlanModal: React.FC<IProps> = ({ onClose, onConfirm, onNotNow, confirmLoading }) => {
  const onConfirmModal = () => onConfirm?.();
  const onNotNowModal = () => onNotNow?.();
  return (
    <Modal size="md" onClose={onClose}>
      <ModalBody>
        <ModalBodyContainer>
          <ModalHeading>Cancel subscription?</ModalHeading>
          <ModalBodyText>
            You current plan expires on 20 Nov 2022.
            <br />
            You will still be able to use your current plan until it expires.
            <br />
            Are you sure you want to cancel your subscription?
          </ModalBodyText>
          <ButtonsContainer>
            <ConfirmBtn size="lg" onClick={onConfirmModal} isLoading={confirmLoading} disabled={confirmLoading}>
              <BtnText color="#6B6B6F" hide={confirmLoading}>
                <FormattedMessage id="cancelSubscription.modal.btn.confirm" />
              </BtnText>
            </ConfirmBtn>
            <LoadingButton size="lg" onClick={onNotNowModal} disabled={confirmLoading}>
              <BtnText>
                <FormattedMessage id="cancelSubscription.modal.btn.notNow" />
              </BtnText>
            </LoadingButton>
          </ButtonsContainer>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};
