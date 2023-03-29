import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, ModalBody, LoadingButton, CheckBox } from "components";
import { Separator } from "components/Separator";

import { useAsyncActions } from "services/notificationSetting/NotificationSettingService";

interface IProps {
  onClose?: () => void;
  onBillingPage: () => void;
}

const ModalBodyContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 30px;
`;

const ModalHeading = styled.div`
  font-style: normal;
  font-weight: 700;
  font-size: 20px;
  line-height: 29px;
  color: #27272a;
`;

const ModalBodyText = styled.div`
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 22px;
  color: #27272a;
`;

const ButtonsContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
`;

const ModalButton = styled(LoadingButton)`
  min-width: 150px;
`;

const CheckboxContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const CheckboxText = styled.div`
  font-style: normal;
  font-weight: 400;
  font-size: 12px;
  line-height: 19px;
  color: #6b6b6f;
  margin-left: 16px;
  user-select: none;
`;

export const IgnoreNotificationModal: React.FC<IProps> = ({ onClose, onBillingPage }) => {
  const { onIgnoreNotifications } = useAsyncActions();

  const [noPrompt, setNoPrompt] = useState<boolean>(false);
  const [ignoreLoading, setIgnoreLoading] = useState<boolean>(false);
  const onIgnore = () => {
    setIgnoreLoading(true);
    onIgnoreNotifications({ noPrompt })
      .then(() => {
        setIgnoreLoading(false);
        onClose?.();
      })
      .catch(() => {
        setIgnoreLoading(false);
      });
  };

  const onUpgrade = () => {
    onBillingPage();
    onClose?.();
  };
  return (
    <Modal size="sm" onClose={onClose}>
      <ModalBody>
        <ModalBodyContainer>
          <ModalHeading>
            <FormattedMessage id="ignore.notification.modal.heading" />
          </ModalHeading>
          <Separator height="25px" />
          <ModalBodyText>
            <FormattedMessage id="ignore.notification.modal.bodyText" />
          </ModalBodyText>
          <Separator height="40px" />
          <ButtonsContainer>
            <ModalButton size="lg" secondary onClick={onIgnore} isLoading={ignoreLoading}>
              <FormattedMessage id="ignore.notification.modal.ignoreBtnText" />
            </ModalButton>
            <ModalButton size="lg" onClick={onUpgrade}>
              <FormattedMessage id="ignore.notification.modal.upgradeBtnText" />
            </ModalButton>
          </ButtonsContainer>
          <Separator height="40px" />
          <CheckboxContainer>
            <CheckBox checked={noPrompt} onClick={() => setNoPrompt((prev) => !prev)} />
            <CheckboxText>
              <FormattedMessage id="ignore.notification.modal.checkboxText" />
            </CheckboxText>
          </CheckboxContainer>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};
