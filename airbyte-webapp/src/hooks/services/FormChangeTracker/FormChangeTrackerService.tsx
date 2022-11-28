import type { Transition } from "history";

import React, { useCallback, useMemo } from "react";

import { useBlocker } from "hooks/router/useBlocker";

import { useConfirmationModalService } from "../ConfirmationModal";
import { useChangedFormsById } from "./hooks";

export const FormChangeTrackerService: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const blocker = useCallback(
    (tx: Transition) => {
      openConfirmationModal({
        title: "form.discardChanges",
        text: "form.discardChangesConfirmation",
        submitButtonText: "form.discardChanges",
        onSubmit: () => {
          setChangedFormsById({});
          closeConfirmationModal();
          tx.retry();
        },
      });
    },
    [closeConfirmationModal, openConfirmationModal, setChangedFormsById]
  );

  const formsChanged = useMemo(
    () => Object.values(changedFormsById ?? {}).some((formChanged) => formChanged),
    [changedFormsById]
  );

  useBlocker(blocker, formsChanged);

  return <>{children}</>;
};
