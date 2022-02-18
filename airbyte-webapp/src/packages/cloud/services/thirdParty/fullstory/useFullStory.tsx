import { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

import type { User } from "packages/cloud/lib/domain/users";

let inited = false;

const useFullStory = (
  config: FullStory.SnippetOptions,
  enabled: boolean,
  user: User | null
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

  useEffect(() => {
    if (enabled) {
      if (user) {
        // We have a user, so identify that user information against fullstory
        FullStory.identify(user.userId, {
          email: user.email,
          displayName: user.name,
          intercomHash: user.intercomHash,
          status: user.status,
        });
      } else {
        // If there is no user or the user logs out, we anonymize that fullstory session again.
        FullStory.anonymize();
      }
    }
  }, [user]);

  return inited;
};

export default useFullStory;
