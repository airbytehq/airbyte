import { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

let inited = false;

const useFullStory = (config: FullStory.SnippetOptions): boolean => {
  useEffect(() => {
    if (!inited) {
      FullStory.init(config);
      inited = true;
    }
  }, [config]);

  return inited;
};

export default useFullStory;
