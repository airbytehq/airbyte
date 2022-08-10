import { SettingsRoute } from "pages/SettingsPage/SettingsPage";

import { RoutePaths } from "../../../pages/routePaths";

const getPageName = (pathname: string): string => {
  const itemSourcePageRegex = new RegExp(`${RoutePaths.Source}/.*`);
  const itemDestinationPageRegex = new RegExp(`${RoutePaths.Destination}/.*`);
  const itemSourceToDestinationPageRegex = new RegExp(
    `(${RoutePaths.Source}|${RoutePaths.Destination})${RoutePaths.Connection}/.*`
  );

  if (pathname === RoutePaths.Destination) {
    return "Destinations Page";
  }
  if (pathname === RoutePaths.Source) {
    return "Sources Page";
  }
  if (pathname === `${RoutePaths.Source}/${RoutePaths.SourceNew}`) {
    return "Create Source Page";
  }
  if (pathname === `${RoutePaths.Destination}/${RoutePaths.DestinationNew}`) {
    return "Create Destination Page";
  }
  if (
    pathname === `${RoutePaths.Source}/${RoutePaths.ConnectionNew}` ||
    pathname === `${RoutePaths.Destination}/${RoutePaths.ConnectionNew}`
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
  if (pathname === `${RoutePaths.Settings}/${SettingsRoute.Source}`) {
    return "Settings Sources Connectors Page";
  }
  if (pathname === `${RoutePaths.Settings}/${SettingsRoute.Destination}`) {
    return "Settings Destinations Connectors Page";
  }
  if (pathname === `${RoutePaths.Settings}/${SettingsRoute.Configuration}`) {
    return "Settings Configuration Page";
  }
  if (pathname === `${RoutePaths.Settings}/${SettingsRoute.Notifications}`) {
    return "Settings Notifications Page";
  }
  if (pathname === `${RoutePaths.Settings}/${SettingsRoute.Metrics}`) {
    return "Settings Metrics Page";
  }
  if (pathname === RoutePaths.Connections) {
    return "Connections Page";
  }

  return "";
};

export { getPageName };
