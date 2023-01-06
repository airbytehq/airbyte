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
    goToSettingsSourcesTab();
  });
  it("downgrades a source version and updates it through the input", () => {
    editVersionByConnectorName("Postgres", "0.1.0");
    editVersionByConnectorName("Postgres", "0.1.1");
  });
  it("downgrades a source version and updates it through 'upgrade all' button", () => {
    editVersionByConnectorName("Postgres", "0.1.0");
    clickUpgradeAllButton();
  });
});

describe("Destination settings main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
    goToSettingsDestinationTab();
  });
  it("downgrades a destination version and updates it through the input", () => {
    editVersionByConnectorName("Postgres", "0.1.0");
    editVersionByConnectorName("Postgres", "0.1.1");
  });
});
