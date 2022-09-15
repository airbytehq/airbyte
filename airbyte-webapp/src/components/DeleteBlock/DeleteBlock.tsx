import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

import { Button, H5 } from "components";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

import { Card } from "../base/Card";

interface IProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
}

const DeleteBlockComponent = styled(Card)`
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
  const navigate = useNavigate();

  const onDeleteButtonClick = useCallback(() => {
    openConfirmationModal({
      text: `tables.${type}DeleteModalText`,
      title: `tables.${type}DeleteConfirm`,
      submitButtonText: "form.delete",
      onSubmit: async () => {
        await onDelete();
        closeConfirmationModal();
        navigate("../..");
      },
      submitButtonDataId: "delete",
    });
  }, [closeConfirmationModal, onDelete, openConfirmationModal, navigate, type]);

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
