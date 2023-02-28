import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import { Button } from "components/base/Button";
import Modal from "components/Modal";

import useLoadingState from "../../hooks/useLoadingState";

const Content = styled.div`
  width: 585px;
  // font-size: 14px;
  // line-height: 28px;
  //padding: 30px;
`;

const ButtonContent = styled.div`
  margin: 50px 0 36px 0;
  display: flex;
  justify-content: space-around;
  flex-direction: row-reverse;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 12px;
  width: 160px;
  height: 46px;
  border-radius: 6px;
  font-size: 16px;
  color: #27272a;
  font-weight: 500;
  color: #fff;
`;

const Text = styled.div<{
  center?: boolean;
}>`
  white-space: pre-line;
  font-size: 18px;
  line-height: 30px;
  text-align: ${({ center }) => (center ? "center" : "left")};
  padding: ${({ center }) => (center ? "20px 30px" : "0")};
  display: flex;
  justify-content: center;
  align-items: center;
`;

export interface ConfirmationModalProps {
  onClose: () => void;
  title: string;
  text: string;
  submitButtonText: string;
  onSubmit: () => void;
  submitButtonDataId?: string;
  cancelButtonText?: string;
  center?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  center,
  onSubmit,
  submitButtonText,
  submitButtonDataId,
  cancelButtonText,
}) => {
  const { isLoading, startAction } = useLoadingState();
  const onSubmitBtnClick = () => startAction({ action: () => onSubmit() });

  return (
    <Modal onClose={onClose} title={<FormattedMessage id={title} />}>
      <Content>
        <Text center={center}>
          <FormattedMessage id={text} />
        </Text>
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} type="button" secondary disabled={isLoading}>
            <FormattedMessage id={cancelButtonText ?? "form.cancel"} />
          </ButtonWithMargin>
          <LoadingButton danger onClick={onSubmitBtnClick} data-id={submitButtonDataId} isLoading={isLoading}>
            <FormattedMessage id={submitButtonText} />
          </LoadingButton>
        </ButtonContent>
      </Content>
    </Modal>
  );
};
