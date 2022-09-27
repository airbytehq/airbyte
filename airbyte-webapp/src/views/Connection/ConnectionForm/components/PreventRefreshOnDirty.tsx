import { useCallback } from "react";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

export const usePreventRefreshOnDirty = (
  dirty: boolean,
  refreshSourceSchema: (refreshSchema?: boolean) => Promise<void>
) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  return useCallback(() => {
    if (dirty) {
      openConfirmationModal({
        title: "connection.updateSchema.formChanged.title",
        text: "connection.updateSchema.formChanged.text",
        submitButtonText: "connection.updateSchema.formChanged.confirm",
        onSubmit: () => {
          closeConfirmationModal();
          refreshSourceSchema(true);
        },
      });
    } else {
      refreshSourceSchema(true);
    }
  }, [closeConfirmationModal, dirty, openConfirmationModal, refreshSourceSchema]);
};
