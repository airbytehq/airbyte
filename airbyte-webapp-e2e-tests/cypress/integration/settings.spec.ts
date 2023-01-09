import { connectorsIds } from "commands/common";
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
    editVersionByConnectorName("source", connectorsIds.sources.AwsCloudTrail, "0.1.0");

    goToSettingsSourcesTab();
    editVersionByConnectorName("source", connectorsIds.sources.AwsCloudTrail, "0.1.1");
  });
  it("downgrades a source version and upgrades it through the button", () => {
    goToSettingsSourcesTab();
    editVersionByConnectorName("source", connectorsIds.sources.AwsCloudTrail, "0.1.0");

    goToSettingsSourcesTab();
    editVersionByConnectorName("source", connectorsIds.sources.AwsCloudTrail);
  });

  it("downgrades a source version and upgrades all sources through 'upgrade all' button", () => {
    editVersionByConnectorName("source", connectorsIds.sources.AwsCloudTrail, "0.1.0");
    clickUpgradeAllButton();
  });
});

describe("Destination settings main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });
  it("downgrades a destination version and upgrades it through the input", () => {
    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", connectorsIds.destinations.AwsDatalake, "0.1.0");

    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", connectorsIds.destinations.AwsDatalake, "0.1.1");
  });
  it("downgrades a destination version and upgrades it through the button", () => {
    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", connectorsIds.destinations.AwsDatalake, "0.1.0");

    goToSettingsDestinationTab();
    editVersionByConnectorName("destination", connectorsIds.destinations.AwsDatalake);
  });
});
