import { goToConnectorBuilderPage, testStream } from "pages/connectorBuilderPage";
import {
  assertTestReadItems,
  assertTestReadAuthFailure,
  configureAuth,
  configureGlobals,
  configureStream,
  configurePagination,
  assertMultiPageReadItems,
} from "commands/connectorBuilder";
import { initialSetupCompleted } from "commands/workspaces";

describe("Connector builder", () => {
  before(() => {
    initialSetupCompleted();
    goToConnectorBuilderPage();
  });

  it("Configure basic connector", () => {
    configureGlobals();
    configureStream();
  });

  it("Fail on missing auth", () => {
    testStream();
    assertTestReadAuthFailure();
  });

  it("Succeed on provided auth", () => {
    configureAuth();
    testStream();
    assertTestReadItems();
  });

  it("Pagination", () => {
    configurePagination();
    testStream();
    assertMultiPageReadItems();
  });
});
