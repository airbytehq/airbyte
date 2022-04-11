import type { Transition } from "history";

import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { useBlocker } from "./router/useBlocker";
import { useConfirmationModalService } from "./services/ConfirmationModal";

export const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

const useDiscardFormChangesConfirmation = () => {
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
};

export default useDiscardFormChangesConfirmation;
