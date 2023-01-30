import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { useConfirmationModalService } from "./services/ConfirmationModal";

export function useDeleteModal(type: "source" | "destination" | "connection", onDelete: () => Promise<unknown>) {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const navigate = useNavigate();

  return useCallback(() => {
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
}
