import type { Transition } from "history";

import React, { useCallback } from "react";

import { useBlocker } from "hooks/router/useBlocker";

import { useFormChangeTrackerService } from "./hooks";
import { useConfirmationModalService } from "../ConfirmationModal";

export const FormChangeTrackerService: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { hasFormChanges, clearAllFormChanges } = useFormChangeTrackerService();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const blocker = useCallback(
    (tx: Transition) => {
      openConfirmationModal({
        title: "form.discardChanges",
        text: "form.discardChangesConfirmation",
        submitButtonText: "form.discardChanges",
        onSubmit: () => {
          clearAllFormChanges();
          closeConfirmationModal();
          tx.retry();
        },
      });
    },
    [clearAllFormChanges, closeConfirmationModal, openConfirmationModal]
  );

  useBlocker(blocker, hasFormChanges);

  return <>{children}</>;
};
