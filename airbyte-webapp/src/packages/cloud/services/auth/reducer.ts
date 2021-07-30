import { ActionType, createAction, createReducer } from "typesafe-actions";
import { User } from "./types";

export const actions = {
  startLoading: createAction("START_LOADING")<void>(),
};

type Actions = ActionType<typeof actions>;

type State = {
  inited: boolean;
  currentUser: User | null;
  loading: boolean;
};

export const initialState: State = {
  inited: false,
  currentUser: null,
  loading: false,
};

export const notificationServiceReducer = createReducer<State, Actions>(
  initialState
).handleAction(
  actions.startLoading,
  (state): State => {
    return {
      ...state,
      loading: true,
    };
  }
);
