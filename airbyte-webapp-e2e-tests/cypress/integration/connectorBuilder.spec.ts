import { updateSchemaModalConfirmBtnClick } from "../pages/modals/updateSchemaModal";
import { goToConnectorBuilderPage, testStream } from "pages/connectorBuilderPage";
import { assertTestReadItems, assertTestReadAuthFailure, configureAuth, configureGlobals, configureStreamWithoutAuth, configurePagination, assertMultiPageReadItems } from "commands/connectorBuilder";

describe("Connector builder", () => {
  before(() => {
    goToConnectorBuilderPage();
  });

  it("Configure basic connector", () => {
    configureGlobals();
    configureStreamWithoutAuth();
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
