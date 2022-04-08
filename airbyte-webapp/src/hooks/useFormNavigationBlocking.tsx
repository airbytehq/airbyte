import type { Transition } from "history";

import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { useBlocker } from "./router/useBlocker";
import { useConfirmationModalService } from "./services/ConfirmationModal/ConfirmationModalService";
import { ConfirmationModal } from "./services/ConfirmationModal/types";

export const useBlockingFormsById = createGlobalState<Record<string, boolean>>({});

const useFormNavigationBlocking = () => {
  const [blockingFormsById, setBlockingFormsById] = useBlockingFormsById();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const blocker = useCallback(
    (tx: Transition) => {
      const modalData: ConfirmationModal = {
        title: "Discard changes",
        text: "There are unsaved changes. Are you sure you want to discard your changes?",
        submitButtonText: "Discard changes",
        onSubmit: async () => {
          setBlockingFormsById({});
          closeConfirmationModal();
          tx.retry();
        },
      };

      openConfirmationModal(modalData);
    },
    [closeConfirmationModal, openConfirmationModal, setBlockingFormsById]
  );

  const isFormBlocking = useMemo(
    () => Object.values(blockingFormsById ?? {}).reduce((acc, value) => acc || value, false),
    [blockingFormsById]
  );

  useBlocker(blocker, isFormBlocking);
};

export default useFormNavigationBlocking;
