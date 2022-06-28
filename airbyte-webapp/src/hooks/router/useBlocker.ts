import type { Blocker, History, Transition } from "history";

import { ContextType, useContext, useEffect } from "react";
import { Navigator as BaseNavigator, UNSAFE_NavigationContext as NavigationContext } from "react-router-dom";

interface Navigator extends BaseNavigator {
  block: History["block"];
}

type NavigationContextWithBlock = ContextType<typeof NavigationContext> & { navigator: Navigator };

/**
 * @source https://github.com/remix-run/react-router/commit/256cad70d3fd4500b1abcfea66f3ee622fb90874
 */
export const useBlocker = (blocker: Blocker, block = true) => {
  const { navigator } = useContext(NavigationContext) as NavigationContextWithBlock;

  useEffect(() => {
    if (!block) {
      return;
    }

    const unblock = navigator.block((tx: Transition) => {
      const autoUnblockingTx = {
        ...tx,
        retry() {
          // Automatically unblock the transition so it can play all the way
          // through before retrying it. TODO: Figure out how to re-enable
          // this block if the transition is cancelled for some reason.
          unblock();
          tx.retry();
        },
      };

      blocker(autoUnblockingTx);
    });

    return unblock;
  }, [navigator, blocker, block]);
};
