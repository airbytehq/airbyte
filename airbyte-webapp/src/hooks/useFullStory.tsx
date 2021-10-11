import { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

let inited = false;

const useFullStory = (config: FullStory.SnippetOptions): boolean => {
  useEffect(() => {
    if (!inited) {
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
