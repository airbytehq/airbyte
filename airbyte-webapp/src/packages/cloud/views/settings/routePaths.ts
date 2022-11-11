import { SettingsRoute } from "pages/SettingsPage/SettingsPage";

export const CloudSettingsRoutes = {
  Configuration: SettingsRoute.Configuration,
  Notifications: SettingsRoute.Notifications,
  Account: SettingsRoute.Account,
  Source: SettingsRoute.Source,
  Destination: SettingsRoute.Destination,
  DataResidency: SettingsRoute.DataResidency,

  Workspace: "workspaces",
  AccessManagement: "access-management",
  DbtCloud: "dbt-cloud",
} as const;
