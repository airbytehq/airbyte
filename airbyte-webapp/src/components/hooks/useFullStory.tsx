import { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

const useFullStory = (config: FullStory.SnippetOptions): void => {
  useEffect(() => {
    FullStory.init(config);
  }, [config]);
};

export default useFullStory;
