import React, { FC } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import Modal from "components/Modal";

import useLoadingState from "../../hooks/useLoadingState";
import { ModalTypes } from "./types";

export type IProps = {
  onClose: () => void;
  onSubmit: (data?: unknown) => void;
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
const ButtonWithMargin = styled(LoadingButton)`
  margin-right: 9px;
`;

interface IModalTextProps {
  modalType: ModalTypes | undefined;
}
const ModalText: FC<IModalTextProps> = ({ modalType }) => {
  if (modalType === ModalTypes.RESET_CHANGED_COLUMN) {
    return <FormattedMessage id="form.changedColumns" />;
  }

  if (modalType === ModalTypes.UPDATE_SCHEMA) {
    return <FormattedMessage id="connection.updateSchemaText" />;
  }

  return <FormattedMessage id="form.resetDataText" />;
};

const ResetDataModal: React.FC<IProps> = ({ onClose, onSubmit, modalType }) => {
  const { isLoading, startAction } = useLoadingState();
  const onSubmitBtnClick = () => startAction({ action: () => onSubmit() });

  const modalTitle =
    modalType === ModalTypes.UPDATE_SCHEMA ? (
      <FormattedMessage id="connection.updateSchema" />
    ) : (
      <FormattedMessage id="form.resetData" />
    );

  const modalCancelButtonText =
    modalType === ModalTypes.UPDATE_SCHEMA ? (
      <FormattedMessage id="form.cancel" />
    ) : (
      <FormattedMessage id="form.noNeed" />
    );

  const modalSubmitButtonText =
    modalType === ModalTypes.UPDATE_SCHEMA ? (
      <FormattedMessage id="connection.updateSchema" />
    ) : (
      <FormattedMessage id="form.reset" />
    );

  return (
    <Modal onClose={onClose} title={modalTitle}>
      <Content>
        <ModalText modalType={modalType} />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary disabled={isLoading}>
            {modalCancelButtonText}
          </ButtonWithMargin>
          <LoadingButton onClick={onSubmitBtnClick} isLoading={isLoading} disabled={isLoading}>
            {modalSubmitButtonText}
          </LoadingButton>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default ResetDataModal;
