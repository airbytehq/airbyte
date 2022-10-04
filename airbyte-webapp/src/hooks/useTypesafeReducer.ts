/* eslint-disable @typescript-eslint/no-explicit-any */
import { Reducer, useReducer, useMemo } from "react";
import { ActionType } from "typesafe-actions";

function useTypesafeReducer<StateShape, Actions extends Record<string, (...args: any[]) => any>>(
  reducer: Reducer<StateShape, ActionType<Actions>>,
  initialState: StateShape,
  actions: Actions
): [StateShape, Actions] {
  const [state, dispatch] = useReducer(reducer, initialState);
  const boundActions = useMemo(() => {
    function bindActionCreator(actionCreator: (...args: any[]) => any, dispatcher: typeof dispatch) {
      return function (this: any) {
        return dispatcher(
          // eslint-disable-next-line prefer-rest-params
          actionCreator.apply(this, arguments as any as any[])
        );
      };
    }

    const newActions = Object.keys(actions).reduce((a, action) => {
      a[action] = bindActionCreator(actions[action], dispatch);
      return a;
    }, {} as Record<string, (...args: any[]) => any>);
    return newActions;
  }, [dispatch, actions]);
  return [state, boundActions as Actions];
}

export default useTypesafeReducer;
