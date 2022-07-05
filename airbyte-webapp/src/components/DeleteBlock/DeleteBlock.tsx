import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, H5 } from "components";
import ContentCard from "components/ContentCard";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import useRouter from "hooks/useRouter";

interface IProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
}

const DeleteBlockComponent = styled(ContentCard)`
  margin-top: 12px;
  padding: 19px 20px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
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
    <DeleteBlockComponent>
      <Text>
        <H5 bold>
          <FormattedMessage id={`tables.${type}Delete.title`} />
        </H5>
        <FormattedMessage id={`tables.${type}DataDelete`} />
      </Text>
      <Button danger onClick={onDeleteButtonClick} data-id="open-delete-modal">
        <FormattedMessage id={`tables.${type}Delete`} />
      </Button>
    </DeleteBlockComponent>
  );
};

export default DeleteBlock;
