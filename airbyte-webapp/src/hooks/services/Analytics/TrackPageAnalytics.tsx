import React, { useEffect } from "react";

import useRouter from "hooks/useRouter";

import { useAnalyticsService } from "./useAnalyticsService";
import { getPageName } from "./pageNameUtils";

export const TrackPageAnalytics: React.FC = () => {
  const { pathname } = useRouter();
  const analyticsService = useAnalyticsService();
  useEffect(() => {
    const pathWithoutWorkspaceId = pathname.split("/").splice(2).join(".");
    const pageName = getPageName(pathWithoutWorkspaceId);
    if (pageName) {
      analyticsService.page(pageName);
    }
  }, [analyticsService, pathname]);

  return null;
};
