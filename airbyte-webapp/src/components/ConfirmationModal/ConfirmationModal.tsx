import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/base/Button";
import Modal from "components/Modal";

const Content = styled.div`
  width: 585px;
  font-size: 14px;
  line-height: 28px;
  padding: 25px;
  white-space: pre-line;
`;

const ButtonContent = styled.div`
  margin-top: 26px;
  display: flex;
  justify-content: flex-end;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 12px;
`;

export interface ConfirmationModalProps {
  onClose: () => void;
  title: string;
  text: string;
  submitButtonText: string;
  onSubmit: () => void;
  submitButtonDataId?: string;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  onSubmit,
  submitButtonText,
  submitButtonDataId,
}) => (
  <Modal onClose={onClose} title={<FormattedMessage id={title} />}>
    <Content>
      <FormattedMessage id={text} />
      <ButtonContent>
        <ButtonWithMargin onClick={onClose} type="button" secondary>
          <FormattedMessage id="form.cancel" />
        </ButtonWithMargin>
        <Button type="button" danger onClick={onSubmit} data-id={submitButtonDataId}>
          <FormattedMessage id={submitButtonText} />
        </Button>
      </ButtonContent>
    </Content>
  </Modal>
);
