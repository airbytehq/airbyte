import React, { useEffect } from "react";

import useRouter from "hooks/useRouter";
import { useAnalytics } from "hooks/useAnalytics";
import { Routes } from "./routes";

const getPageName = (pathname: string) => {
  const itemSourcePageRegex = new RegExp(`${Routes.Source}/.*`);
  const itemDestinationPageRegex = new RegExp(`${Routes.Destination}/.*`);
  const itemSourceToDestinationPageRegex = new RegExp(
    `(${Routes.Source}|${Routes.Destination})${Routes.Connection}/.*`
  );

  if (pathname === Routes.Destination) {
    return "Destinations Page";
  }
  if (pathname === Routes.Root) {
    return "Sources Page";
  }
  if (pathname === `${Routes.Source}${Routes.SourceNew}`) {
    return "Create Source Page";
  }
  if (pathname === `${Routes.Destination}${Routes.DestinationNew}`) {
    return "Create Destination Page";
  }
  if (
    pathname === `${Routes.Source}${Routes.ConnectionNew}` ||
    pathname === `${Routes.Destination}${Routes.ConnectionNew}`
  ) {
    return "Create Connection Page";
  }
  if (pathname.match(itemSourceToDestinationPageRegex)) {
    return "Source to Destination Page";
  }
  if (pathname.match(itemDestinationPageRegex)) {
    return "Destination Item Page";
  }
  if (pathname.match(itemSourcePageRegex)) {
    return "Source Item Page";
  }
  if (pathname === `${Routes.Settings}${Routes.Source}`) {
    return "Settings Sources Connectors Page";
  }
  if (pathname === `${Routes.Settings}${Routes.Destination}`) {
    return "Settings Destinations Connectors Page";
  }
  if (pathname === `${Routes.Settings}${Routes.Configuration}`) {
    return "Settings Configuration Page";
  }
  if (pathname === `${Routes.Settings}${Routes.Notifications}`) {
    return "Settings Notifications Page";
  }
  if (pathname === `${Routes.Settings}${Routes.Metrics}`) {
    return "Settings Metrics Page";
  }
  if (pathname === Routes.Connections) {
    return "Connections Page";
  }

  return "";
};

export const WithPageAnalytics: React.FC = () => {
  const { pathname } = useRouter();
  const analyticsService = useAnalytics();
  useEffect(() => {
    const pageName = getPageName(pathname);
    if (pageName) {
      analyticsService.page(pageName);
    }
  }, [analyticsService, pathname]);

  return null;
};
