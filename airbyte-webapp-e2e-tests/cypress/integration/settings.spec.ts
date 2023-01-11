// import { connectorsIds } from "commands/common";
import { ConnectorIds } from "../../../airbyte-webapp/src/utils/connectors/constants";
import { initialSetupCompleted } from "commands/workspaces";
import {
  clickUpgradeAllButton,
  editVersionByConnectorName,
  goToSettingsDestinationTab,
  goToSettingsSourcesTab,
} from "pages/settingsPage";

describe("Source settings main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });
  it("downgrades a source version and upgrades it through the input", () => {
    goToSettingsSourcesTab();
    editVersionByConnectorName("source", ConnectorIds.Sources.AwsCloudTrail, "0.1.0");

    goToSettingsSourcesTab();
    editVersionByConnectorName("source", ConnectorIds.Sources.AwsCloudTrail, "0.1.1");
  });
  it("downgrades a source version and upgrades it through the button", () => {
    goToSettingsSourcesTab();
    editVersionByConnectorName("source", ConnectorIds.Sources.AwsCloudTrail, "0.1.0");

    goToSettingsSourcesTab();
    editVersionByConnectorName("source", ConnectorIds.Sources.AwsCloudTrail);
  });

  it("downgrades a source version and upgrades all sources through 'upgrade all' button", () => {
    editVersionByConnectorName("source", ConnectorIds.Sources.AwsCloudTrail, "0.1.0");
    clickUpgradeAllButton();
  });
});

describe("Destination settings main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });
  it("downgrades a destination version and upgrades it through the input", () => {
    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", ConnectorIds.Destinations.AwsDatalake, "0.1.0");

    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", ConnectorIds.Destinations.AwsDatalake, "0.1.1");
  });
  it("downgrades a destination version and upgrades it through the button", () => {
    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", ConnectorIds.Destinations.AwsDatalake, "0.1.0");

    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", ConnectorIds.Destinations.AwsDatalake);
  });
});
