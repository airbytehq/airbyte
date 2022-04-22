import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import Modal from "components/Modal";

import { ModalTypes } from "./types";

export type IProps = {
  onClose: () => void;
  onSubmit: (data: unknown) => void;
  modalType?: ModalTypes;
};

const Content = styled.div`
  padding: 18px 37px 28px;
  font-size: 14px;
  line-height: 28px;
  max-width: 585px;
`;
const ButtonContent = styled.div`
  padding-top: 27px;
  text-align: right;
`;
const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const ResetDataModal: React.FC<IProps> = ({ onClose, onSubmit, modalType }) => {
  const modalText = () => {
    if (modalType === ModalTypes.RESET_CHANGED_COLUMN) {
      return <FormattedMessage id="form.changedColumns" />;
    }

    if (modalType === ModalTypes.UPDATE_SCHEMA) {
      return <FormattedMessage id="connection.updateSchemaText" />;
    }

    return <FormattedMessage id="form.resetDataText" />;
  };

  const modalTitle = () => {
    if (modalType === ModalTypes.UPDATE_SCHEMA) {
      return <FormattedMessage id="connection.updateSchema" />;
    }

    return <FormattedMessage id="form.resetData" />;
  };

  const modalCancelButtonText = () => {
    if (modalType === ModalTypes.UPDATE_SCHEMA) {
      return <FormattedMessage id="form.cancel" />;
    }

    return <FormattedMessage id="form.noNeed" />;
  };

  const modalSubmitButtonText = () => {
    if (modalType === ModalTypes.UPDATE_SCHEMA) {
      return <FormattedMessage id="connection.updateSchema" />;
    }

    return <FormattedMessage id="form.reset" />;
  };

  return (
    <Modal onClose={onClose} title={modalTitle()}>
      <Content>
        {modalText()}
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary>
            {modalCancelButtonText()}
          </ButtonWithMargin>
          <Button onClick={onSubmit}>{modalSubmitButtonText()}</Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default ResetDataModal;
