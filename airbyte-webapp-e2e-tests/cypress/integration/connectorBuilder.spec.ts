import { goToConnectorBuilderPage, testStream } from "pages/connectorBuilderPage";
import { assertTestReadItems, assertTestReadAuthFailure, configureAuth, configureGlobals, configureStream, configurePagination, assertMultiPageReadItems } from "commands/connectorBuilder";

describe("Connector builder", () => {
  before(() => {
    goToConnectorBuilderPage();
  });

  test("Configure basic connector", () => {
    configureGlobals();
    configureStream();
  });

  test("Fail on missing auth", () => {
    testStream();
    assertTestReadAuthFailure();
  });

  test("Succeed on provided auth", () => {
    configureAuth();
    testStream();
    assertTestReadItems();
  });

  test("Pagination", () => {
    configurePagination();
    testStream();
    assertMultiPageReadItems();
  });
});
