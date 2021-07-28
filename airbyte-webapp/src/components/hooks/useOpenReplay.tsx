import { useMemo } from "react";
import Tracker, { Options } from "@asayerio/tracker";

let tracker: Tracker | null = null;

const useTracker = (options: Options): Tracker => {
  return useMemo(() => {
    if (!tracker) {
      tracker = new Tracker(options);

      tracker.start();
    }

    return tracker;
  }, [options]);
};

export default useTracker;
