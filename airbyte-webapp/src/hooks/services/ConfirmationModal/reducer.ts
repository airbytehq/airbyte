import { ActionType, createAction, createReducer } from "typesafe-actions";

import { ConfirmationModalOptions, ConfirmationModalState } from "./types";

export const actions = {
  openConfirmationModal: createAction("OPEN_CONFIRMATION_MODAL")<ConfirmationModalOptions>(),
  closeConfirmationModal: createAction("CLOSE_CONFIRMATION_MODAL")(),
};

type Actions = ActionType<typeof actions>;

export const initialState: ConfirmationModalState = {
  isOpen: false,
  confirmationModal: null,
};

export const confirmationModalServiceReducer = createReducer<ConfirmationModalState, Actions>(initialState)
  .handleAction(actions.openConfirmationModal, (state, action): ConfirmationModalState => {
    return {
      ...state,
      isOpen: true,
      confirmationModal: action.payload,
    };
  })
  .handleAction(actions.closeConfirmationModal, (state): ConfirmationModalState => {
    return {
      ...state,
      isOpen: false,
      confirmationModal: null,
    };
  });
