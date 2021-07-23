import { useMemo } from "react";
import OpenReplay from "@openreplay/tracker";

let tracker: OpenReplay | null = null;

const useOpenReplay = (projectKey: string): OpenReplay => {
  return useMemo(() => {
    if (!tracker) {
      tracker = new OpenReplay({
        projectKey,
      });

      tracker.start();
    }

    return tracker;
  }, [projectKey]);
};

export default useOpenReplay;
