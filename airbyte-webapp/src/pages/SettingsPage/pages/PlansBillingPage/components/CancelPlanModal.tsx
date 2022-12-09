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

const ConfirmBtn = styled(Button)`
  background-color: ${({ theme }) => theme.white};
  color: #6b6b6f;
  border: 1px solid #d1d5db;
`;

const BtnText = styled.div<{
  color?: string;
}>`
  font-weight: 500;
  font-size: 14px;
  color: ${({ theme, color }) => (color ? color : theme.white)};
`;

export const CancelPlanModal: React.FC<IProps> = ({ onClose }) => {
  const onConfirm = () => onClose?.();
  const onNotNow = () => onClose?.();
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
            <ConfirmBtn size="lg" onClick={onConfirm}>
              <BtnText color="#6B6B6F">
                <FormattedMessage id="cancelSubscription.modal.btn.confirm" />
              </BtnText>
            </ConfirmBtn>
            <Button size="lg" onClick={onNotNow}>
              <BtnText>
                <FormattedMessage id="cancelSubscription.modal.btn.notNow" />
              </BtnText>
            </Button>
          </ButtonsContainer>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};
