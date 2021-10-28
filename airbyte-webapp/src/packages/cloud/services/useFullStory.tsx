import { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

let inited = false;

const useFullStory = (
  config: FullStory.SnippetOptions,
  enabled: boolean
): boolean => {
  useEffect(() => {
    if (!inited && enabled) {
      try {
        FullStory.init(config);
        inited = true;
      } catch (e) {
        console.error("Failed to init Full Story");
      }
    }
  }, [config]);

  return inited;
};

export default useFullStory;
