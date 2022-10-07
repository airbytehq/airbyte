import { useCallback } from "react";
import { useUnmount } from "react-use";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";

export const useRefreshSourceSchemaWithConfirmationOnDirty = (dirty: boolean) => {
  const { clearFormChange } = useFormChangeTrackerService();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { formId, refreshSchema } = useConnectionFormService();

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
          clearFormChange(formId);
          refreshSchema();
        },
      });
    } else {
      refreshSchema();
    }
  }, [clearFormChange, closeConfirmationModal, dirty, formId, openConfirmationModal, refreshSchema]);
};
