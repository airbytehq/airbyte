import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Modal from "../../../../../components/Modal";
import Button from "../../../../../components/Button";

export type IProps = {
  onClose: () => void;
  onSubmit: () => void;
};

const Content = styled.div`
  width: 585px;
  font-size: 14px;
  line-height: 28px;
  padding: 10px 40px 15px 37px;
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

const DeleteModal: React.FC<IProps> = ({ onClose, onSubmit }) => {
  return (
    <Modal
      onClose={onClose}
      title={<FormattedMessage id="sources.deleteConfirm" />}
    >
      <Content>
        <FormattedMessage id="sources.deleteModalText" />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </ButtonWithMargin>
          <Button type="button" danger onClick={onSubmit}>
            <FormattedMessage id="form.delete" />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default DeleteModal;
