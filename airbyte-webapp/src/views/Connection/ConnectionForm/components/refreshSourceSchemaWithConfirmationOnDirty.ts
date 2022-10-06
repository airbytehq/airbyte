import { useCallback } from "react";
import { useUnmount } from "react-use";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

export const useRefreshSourceSchemaWithConfirmationOnDirty = (dirty: boolean) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { refreshSchema } = useConnectionFormService();

  useUnmount(() => {
    closeConfirmationModal();
  });

  return useCallback(() => {
    if (dirty) {
      openConfirmationModal({
        title: "connection.updateSchema.formChanged.title",
        text: "connection.updateSchema.formChanged.text",
        submitButtonText: "connection.updateSchema.formChanged.confirm",
        onSubmit: () => {
          closeConfirmationModal();
          refreshSchema();
        },
      });
    } else {
      refreshSchema();
    }
  }, [closeConfirmationModal, dirty, openConfirmationModal, refreshSchema]);
};
