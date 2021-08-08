import { ActionType, createAction, createReducer } from "typesafe-actions";
import { User } from "packages/cloud/lib/domain/users";

export const actions = {
  authInited: createAction("AUTH_INITED")<void>(),
  loggedIn: createAction("LOGGED_IN")<User>(),
  loggedOut: createAction("LOGGED_OUT")<void>(),
};

type Actions = ActionType<typeof actions>;

export type AuthServiceState = {
  inited: boolean;
  currentUser: User | null;
  loading: boolean;
};

export const initialState: AuthServiceState = {
  inited: false,
  currentUser: null,
  loading: false,
};

export const authStateReducer = createReducer<AuthServiceState, Actions>(
  initialState
)
  .handleAction(
    actions.authInited,
    (state): AuthServiceState => {
      return {
        ...state,
        inited: true,
      };
    }
  )
  .handleAction(
    actions.loggedIn,
    (state, action): AuthServiceState => {
      return {
        ...state,
        currentUser: action.payload,
        inited: true,
        loading: false,
      };
    }
  )
  .handleAction(
    actions.loggedOut,
    (state): AuthServiceState => {
      return {
        ...state,
        currentUser: null,
      };
    }
  );
