import { initialSetupCompleted } from "commands/workspaces";
import {
  getPostgresCreateDestinationBody,
  getPostgresCreateSourceBody,
  requestCreateDestination,
  requestCreateSource,
  requestDeleteConnection,
  requestDeleteDestination,
  requestDeleteSource,
  requestWorkspaceId,
} from "commands/api";
import { appendRandomString, submitButtonClick } from "commands/common";
import * as connectionListPage from "pages/connection/connectionListPageObject";
import * as newConnectionPage from "pages/connection/createConnectionPageObject";
import {
  interceptCreateConnectionRequest,
  interceptDiscoverSchemaRequest,
  interceptGetSourceDefinitionsRequest,
  interceptGetSourcesListRequest,
  waitForCreateConnectionRequest,
  waitForDiscoverSchemaRequest,
  waitForGetSourceDefinitionsRequest,
  waitForGetSourcesListRequest,
} from "commands/interceptors";
import { Connection, Destination, Source } from "commands/api/types";
import * as replicationPage from "pages/connection/connectionFormPageObject";
import { runDbQuery } from "commands/db/db";
import {
  createUsersTableQuery,
  dropUsersTableQuery,
  createDummyTablesQuery,
  dropDummyTablesQuery,
} from "commands/db/queries";
import streamsTablePageObject from "pages/connection/streamsTablePageObject";

// TODO: Enable this test when the new stream table will be turned on
describe.skip("Connection - Create new connection", () => {
  let source: Source;
  let destination: Destination;
  let connectionId: string;

  before(() => {
    initialSetupCompleted();
    runDbQuery(dropUsersTableQuery);
    runDbQuery(dropDummyTablesQuery(20));

    runDbQuery(createUsersTableQuery);
    runDbQuery(createDummyTablesQuery(20));

    requestWorkspaceId().then(() => {
      const sourceRequestBody = getPostgresCreateSourceBody(appendRandomString("Stream table Source"));
      const destinationRequestBody = getPostgresCreateDestinationBody(appendRandomString("Stream table Destination"));

      requestCreateSource(sourceRequestBody).then((sourceResponse) => {
        source = sourceResponse;
        requestCreateDestination(destinationRequestBody).then((destinationResponse) => {
          destination = destinationResponse;
        });
      });
    });
  });

  after(() => {
    if (connectionId) {
      requestDeleteConnection(connectionId);
    }
    if (source) {
      requestDeleteSource(source.sourceId);
    }
    if (destination) {
      requestDeleteDestination(destination.destinationId);
    }
  });

  describe("Set up source and destination", () => {
    it("should open 'New connection' page", () => {
      connectionListPage.visit();
      interceptGetSourcesListRequest();
      interceptGetSourceDefinitionsRequest();

      connectionListPage.clickNewConnectionButton();
      waitForGetSourcesListRequest();
      waitForGetSourceDefinitionsRequest();
    });

    it("should select existing Source from dropdown and click button", () => {
      newConnectionPage.selectExistingConnectorFromDropdown(source.name);
      newConnectionPage.clickUseExistingConnectorButton("source");
    });

    it("should select existing Destination from dropdown and click button", () => {
      interceptDiscoverSchemaRequest();
      newConnectionPage.selectExistingConnectorFromDropdown(destination.name);
      newConnectionPage.clickUseExistingConnectorButton("destination");
      waitForDiscoverSchemaRequest();
    });

    it("should redirect to 'New connection' settings page with stream table'", () => {
      newConnectionPage.isAtNewConnectionPage();
    });

    it("should show 'New connection' page header", () => {
      newConnectionPage.isNewConnectionPageHeaderVisible();
    });
  });

  describe("Configuration", () => {
    it("should set 'Replication frequency' to 'Manual'", () => {
      replicationPage.selectSchedule("Manual");
    });
  });

  describe("Streams table", () => {
    it("should check check connector icons and titles in table", () => {
      newConnectionPage.checkConnectorIconAndTitle("source");
      newConnectionPage.checkConnectorIconAndTitle("destination");
    });

    it("should check columns names in table", () => {
      newConnectionPage.checkColumnNames();
    });

    it("should check total amount of table streams", () => {
      // dummy tables amount + users table
      newConnectionPage.checkAmountOfStreamTableRows(21);
    });

    it("should allow to scroll table to desired stream table row and it should be visible", () => {
      const desiredStreamTableRow = "dummy_table_18";

      newConnectionPage.scrollTableToStream(desiredStreamTableRow);
      newConnectionPage.isStreamTableRowVisible(desiredStreamTableRow);
    });

    it("should filter table by stream name", () => {
      streamsTablePageObject.searchStream("dummy_table_10");
      newConnectionPage.checkAmountOfStreamTableRows(1);
    });

    it("should clear stream search input field and show all available streams", () => {
      streamsTablePageObject.clearStreamSearch();
      newConnectionPage.checkAmountOfStreamTableRows(21);
    });
  });

  /*
    here will be added more tests to extend the test flow
   */

  describe("Submit form", () => {
    it("should set up a connection", () => {
      interceptCreateConnectionRequest();
      submitButtonClick(true);

      waitForCreateConnectionRequest().then((interception) => {
        assert.isNotNull(interception.response?.statusCode, "200");
        expect(interception.request.method).to.eq("POST");

        const connection: Partial<Connection> = {
          name: `${source.name} <> ${destination.name}`,
          scheduleType: "manual",
        };
        expect(interception.request.body).to.contain(connection);
        expect(interception.response?.body).to.contain(connection);

        connectionId = interception.response?.body?.connectionId;
      });
    });

    it("should redirect to connection overview page after connection set up", () => {
      newConnectionPage.isAtConnectionOverviewPage(connectionId);
    });
  });
});
