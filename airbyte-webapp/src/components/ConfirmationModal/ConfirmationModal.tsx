import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Modal from "components/Modal";
import { Button } from "components/base/Button";

const Content = styled.div`
  width: 585px;
  font-size: 14px;
  line-height: 28px;
  padding: 25px;
  white-space: pre-line;
`;

const ButtonContent = styled.div`
  padding-top: 28px;
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
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  onSubmit,
  submitButtonText,
}) => (
  <Modal onClose={onClose} title={<FormattedMessage id={title} />}>
    <Content>
      <FormattedMessage id={text} />
      <ButtonContent>
        <ButtonWithMargin onClick={onClose} type="button" secondary>
          <FormattedMessage id="form.cancel" />
        </ButtonWithMargin>
        <Button type="button" danger onClick={onSubmit} data-id="delete">
          <FormattedMessage id={submitButtonText} />
        </Button>
      </ButtonContent>
    </Content>
  </Modal>
);
