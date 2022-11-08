import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

import { DeleteBlockProps } from "./interfaces";

export const useDeleteModal = ({ type, onDelete }: Partial<DeleteBlockProps>): { onDeleteButtonClick: () => void } => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const navigate = useNavigate();

  const onDeleteButtonClick = useCallback(() => {
    if (!onDelete) {
      return;
    }
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

  return {
    onDeleteButtonClick,
  };
};
