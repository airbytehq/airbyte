import React, { useContext, useEffect, useMemo } from "react";

import { ConfirmationModal } from "components/ConfirmationModal";

import useTypesafeReducer from "hooks/useTypesafeReducer";

import { actions, initialState, confirmationModalServiceReducer } from "./reducer";
import { ConfirmationModalOptions, ConfirmationModalServiceApi, ConfirmationModalState } from "./types";

const ConfirmationModalServiceContext = React.createContext<ConfirmationModalServiceApi | undefined>(undefined);

export const useConfirmationModalService: (confirmationModal?: ConfirmationModalOptions) => {
  openConfirmationModal: (confirmationModal: ConfirmationModalOptions) => void;
  closeConfirmationModal: () => void;
} = (confirmationModal) => {
  const confirmationModalService = useContext(ConfirmationModalServiceContext);
  if (!confirmationModalService) {
    throw new Error("useConfirmationModalService must be used within a ConfirmationModalService.");
  }

  useEffect(() => {
    if (confirmationModal) {
      confirmationModalService.openConfirmationModal(confirmationModal);
    }
    return () => {
      if (confirmationModal) {
        confirmationModalService.closeConfirmationModal();
      }
    };
  }, [confirmationModal, confirmationModalService]);

  return useMemo(
    () => ({
      openConfirmationModal: confirmationModalService.openConfirmationModal,
      closeConfirmationModal: confirmationModalService.closeConfirmationModal,
    }),
    [confirmationModalService]
  );
};

export const ConfirmationModalService = ({ children }: { children: React.ReactNode }) => {
  const [state, { openConfirmationModal, closeConfirmationModal }] = useTypesafeReducer<
    ConfirmationModalState,
    typeof actions
  >(confirmationModalServiceReducer, initialState, actions);

  const confirmationModalService: ConfirmationModalServiceApi = useMemo(
    () => ({
      openConfirmationModal,
      closeConfirmationModal,
    }),
    [closeConfirmationModal, openConfirmationModal]
  );

  return (
    <>
      <ConfirmationModalServiceContext.Provider value={confirmationModalService}>
        {children}
      </ConfirmationModalServiceContext.Provider>
      {state.isOpen && state.confirmationModal ? (
        <ConfirmationModal
          onClose={closeConfirmationModal}
          title={state.confirmationModal.title}
          text={state.confirmationModal.text}
          onSubmit={state.confirmationModal.onSubmit}
          submitButtonText={state.confirmationModal.submitButtonText}
          submitButtonDataId={state.confirmationModal.submitButtonDataId}
          cancelButtonText={state.confirmationModal.cancelButtonText}
        />
      ) : null}
    </>
  );
};
