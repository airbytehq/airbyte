import React, { useContext, useEffect, useMemo } from "react";

import ConfirmationModalComponent from "components/ConfirmationModal";

import {
  ConfirmationModal,
  ConfirmationModalServiceApi,
  ConfirmationModalState,
} from "./types";
import useTypesafeReducer from "hooks/useTypesafeReducer";
import {
  actions,
  initialState,
  confirmationModalServiceReducer,
} from "./reducer";

const confirmationModalServiceContext = React.createContext<ConfirmationModalServiceApi | null>(
  null
);

function ConfirmationModalService({ children }: { children: React.ReactNode }) {
  const [
    state,
    { openConfirmationModal, closeConfirmationModal },
  ] = useTypesafeReducer<ConfirmationModalState, typeof actions>(
    confirmationModalServiceReducer,
    initialState,
    actions
  );

  const confirmationModalService: ConfirmationModalServiceApi = useMemo(
    () => ({
      openConfirmationModal,
      closeConfirmationModal,
    }),
    []
  );

  return (
    <>
      <confirmationModalServiceContext.Provider
        value={confirmationModalService}
      >
        {children}
      </confirmationModalServiceContext.Provider>
      {state.isOpen && state.confirmationModal ? (
        <ConfirmationModalComponent
          onClose={closeConfirmationModal}
          title={state.confirmationModal.title}
          text={state.confirmationModal.text}
          onSubmit={state.confirmationModal.onSubmit}
          submitButtonText={state.confirmationModal.submitButtonText}
        />
      ) : null}
    </>
  );
}

export const useConfirmationModalService: (
  confirmationModal?: ConfirmationModal,
  dependencies?: []
) => {
  openConfirmationModal: (confirmationModal: ConfirmationModal) => void;
  closeConfirmationModal: () => void;
} = (confirmationModal, dependencies) => {
  const confirmationModalService = useContext(confirmationModalServiceContext);
  if (!confirmationModalService) {
    throw new Error(
      "useConfirmationModalService must be used within a ConfirmationModalService."
    );
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
    // eslint-disable-next-line
  }, [confirmationModal, confirmationModalService, ...(dependencies || [])]);

  return {
    openConfirmationModal: confirmationModalService.openConfirmationModal,
    closeConfirmationModal: confirmationModalService.closeConfirmationModal,
  };
};

export default React.memo(ConfirmationModalService);
