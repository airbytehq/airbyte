import type { Transition } from "history";

import React, { useCallback } from "react";

import { useBlocker } from "hooks/router/useBlocker";

import { useConfirmationModalService } from "../ConfirmationModal";
import { useFormChangeTrackerService } from "./hooks";

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
