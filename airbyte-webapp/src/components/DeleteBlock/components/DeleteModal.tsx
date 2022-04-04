import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Modal from "components/Modal";
import { Button, LoadingButton } from "components";
import { useMutation } from "react-query";
export type IProps = {
  onClose: () => void;
  onSubmit: () => Promise<unknown>;
  type: "source" | "destination" | "connection";
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

const DeleteModal: React.FC<IProps> = ({ onClose, onSubmit, type }) => {
  const { isLoading, mutateAsync } = useMutation(() => onSubmit());

  return (
    <Modal
      onClose={onClose}
      title={<FormattedMessage id={`tables.${type}DeleteConfirm`} />}
    >
      <Content>
        <FormattedMessage id={`tables.${type}DeleteModalText`} />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </ButtonWithMargin>
          <LoadingButton
            type="button"
            danger
            isLoading={isLoading}
            onClick={() => mutateAsync()}
            data-id="delete"
          >
            <FormattedMessage id="form.delete" />
          </LoadingButton>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default DeleteModal;
