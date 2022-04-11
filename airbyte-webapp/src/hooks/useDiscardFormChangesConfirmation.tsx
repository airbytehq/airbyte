import type { Transition } from "history";

import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { useBlocker } from "./router/useBlocker";
import { useConfirmationModalService } from "./services/ConfirmationModal";
import { ConfirmationModalOptions } from "./services/ConfirmationModal/types";

export const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

const useDiscardFormChangesConfirmation = () => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const blocker = useCallback(
    (tx: Transition) => {
      const modalData: ConfirmationModalOptions = {
        title: "Discard changes",
        text: "There are unsaved changes. Are you sure you want to discard your changes?",
        submitButtonText: "Discard changes",
        onSubmit: async () => {
          setChangedFormsById({});
          closeConfirmationModal();
          tx.retry();
        },
      };

      openConfirmationModal(modalData);
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
