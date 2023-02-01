import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { useConfirmationModalService } from "./services/ConfirmationModal";

export function useDeleteModal(
  type: "source" | "destination" | "connection",
  onDelete: () => Promise<unknown>,
  additionalContent?: React.ReactNode
) {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const navigate = useNavigate();

  return useCallback(() => {
    openConfirmationModal({
      text: `tables.${type}DeleteModalText`,
      additionalContent,
      title: `tables.${type}DeleteConfirm`,
      submitButtonText: "form.delete",
      onSubmit: async () => {
        await onDelete();
        closeConfirmationModal();
        navigate("../..");
      },
      submitButtonDataId: "delete",
    });
  }, [openConfirmationModal, type, additionalContent, onDelete, closeConfirmationModal, navigate]);
}
