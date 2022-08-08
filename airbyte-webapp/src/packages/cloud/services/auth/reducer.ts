import { ActionType, createAction, createReducer } from "typesafe-actions";

import { User } from "packages/cloud/lib/domain/users";

export const actions = {
  authInited: createAction("AUTH_INITED")<void>(),
  loggedIn: createAction("LOGGED_IN")<{ user: User; emailVerified: boolean; provider: string }>(),
  emailVerified: createAction("EMAIL_VERIFIED")<boolean>(),
  loggedOut: createAction("LOGGED_OUT")<void>(),
  updateUserName: createAction("UPDATE_USER_NAME")<{ value: string }>(),
};

type Actions = ActionType<typeof actions>;

export interface AuthServiceState {
  inited: boolean;
  currentUser: User | null;
  emailVerified: boolean;
  loading: boolean;
  loggedOut: boolean;
  provider: string | null;
}

export const initialState: AuthServiceState = {
  inited: false,
  currentUser: null,
  emailVerified: false,
  loading: false,
  loggedOut: false,
  provider: null,
};

export const authStateReducer = createReducer<AuthServiceState, Actions>(initialState)
  .handleAction(actions.authInited, (state): AuthServiceState => {
    return {
      ...state,
      inited: true,
    };
  })
  .handleAction(actions.loggedIn, (state, action): AuthServiceState => {
    return {
      ...state,
      currentUser: action.payload.user,
      emailVerified: action.payload.emailVerified,
      provider: action.payload.provider,
      inited: true,
      loading: false,
      loggedOut: false,
    };
  })
  .handleAction(actions.emailVerified, (state, action): AuthServiceState => {
    return {
      ...state,
      emailVerified: action.payload,
    };
  })
  .handleAction(actions.loggedOut, (state): AuthServiceState => {
    return {
      ...state,
      currentUser: null,
      emailVerified: false,
      loggedOut: true,
      provider: null,
    };
  })
  .handleAction(actions.updateUserName, (state, action): AuthServiceState => {
    if (!state.currentUser) {
      return state;
    }
    return {
      ...state,
      currentUser: {
        ...state.currentUser,
        name: action.payload.value,
      },
    };
  });
