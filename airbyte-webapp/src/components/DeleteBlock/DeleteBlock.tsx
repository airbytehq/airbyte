import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import useRouter from "hooks/useRouter";

interface IProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
}

const Title = styled.div`
  font-weight: 500;
  font-size: 20px;
  line-height: 30px;
  color: #27272a;
`;

const Text = styled.div`
  font-weight: 500;
  font-size: 15px;
  line-height: 30px;
  color: #999999;
  margin: 16px 0;
  white-space: pre-line;
`;

const DeleteButton = styled(Button)`
  // width: 168px;
  height: 36px;
  background: #ff5454;
  border-radius: 6px;
  border-color: #ff5454;
  font-size: 16px;
  color: #ffffff;
`;

const DeleteBlock: React.FC<IProps> = ({ type, onDelete }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { push } = useRouter();

  const onDeleteButtonClick = useCallback(() => {
    openConfirmationModal({
      text: `tables.${type}DeleteModalText`,
      title: `tables.${type}DeleteConfirm`,
      submitButtonText: "form.delete",
      onSubmit: async () => {
        await onDelete();
        closeConfirmationModal();
        push("../..");
      },
      submitButtonDataId: "delete",
    });
  }, [closeConfirmationModal, onDelete, openConfirmationModal, push, type]);

  return (
    <>
      <Title>
        <FormattedMessage id={`tables.${type}Delete.title`} />
      </Title>
      <Text>
        <FormattedMessage id={`tables.${type}DataDelete`} />
      </Text>
      <DeleteButton danger onClick={onDeleteButtonClick} data-id="open-delete-modal" size="m">
        <FormattedMessage id={`tables.${type}Delete.title`} />
      </DeleteButton>
    </>
  );
};

export default DeleteBlock;
