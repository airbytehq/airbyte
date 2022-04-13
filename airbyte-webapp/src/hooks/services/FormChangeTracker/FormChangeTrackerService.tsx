import type { Transition } from "history";

import React, { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { useBlocker } from "hooks/router/useBlocker";

import { useConfirmationModalService } from "../ConfirmationModal";
import { FormChangeTrackerServiceApi } from "./types";

const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

export const useFormChangeTrackerService = (): FormChangeTrackerServiceApi => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();

  const clearAllFormChanges = useCallback(() => {
    setChangedFormsById({});
  }, [setChangedFormsById]);

  const clearFormChange = useCallback(
    (id: string) => {
      setChangedFormsById({ ...changedFormsById, [id]: false });
    },
    [changedFormsById, setChangedFormsById]
  );

  const trackFormChange = useCallback(
    (id: string, changed: boolean) => {
      if (!!changedFormsById?.[id] !== changed) {
        setChangedFormsById({ ...changedFormsById, [id]: changed });
      }
    },
    [changedFormsById, setChangedFormsById]
  );

  return {
    trackFormChange,
    clearFormChange,
    clearAllFormChanges,
  };
};

export const FormChangeTrackerService: React.FC = ({ children }) => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const blocker = useCallback(
    (tx: Transition) => {
      openConfirmationModal({
        title: "form.discardChanges",
        text: "form.discardChangesConfirmation",
        submitButtonText: "form.discardChanges",
        onSubmit: async () => {
          setChangedFormsById({});
          closeConfirmationModal();
          tx.retry();
        },
      });
    },
    [closeConfirmationModal, openConfirmationModal, setChangedFormsById]
  );

  const formsChanged = useMemo(
    () => Object.values(changedFormsById ?? {}).reduce((acc, value) => acc || value, false),
    [changedFormsById]
  );

  useBlocker(blocker, formsChanged);

  return <>{children}</>;
};
