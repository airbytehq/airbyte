import { useEffect } from "react";
import { useLocation } from "react-router-dom";

import { getPageName } from "./pageNameUtils";
import { useAnalyticsService } from "./useAnalyticsService";

export const useTrackPageAnalytics = () => {
  const { pathname } = useLocation();
  const analyticsService = useAnalyticsService();
  useEffect(() => {
    const pathWithoutWorkspaceId = pathname.split("/").splice(2).join(".");
    const pageName = getPageName(pathWithoutWorkspaceId);
    if (pageName) {
      analyticsService.page(pageName);
    }
  }, [analyticsService, pathname]);
};
