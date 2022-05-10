import { waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Connection, ConnectionNamespaceDefinition, ConnectionStatus } from "core/domain/connection";
import { Destination, Source } from "core/domain/connector";
import { render } from "utils/testutils";

import ConnectionForm from "./ConnectionForm";

const mockSource: Source = {
  sourceId: "test-source",
  name: "test source",
  sourceName: "test-source-name",
  workspaceId: "test-workspace-id",
  sourceDefinitionId: "test-source-definition-id",
  connectionConfiguration: undefined,
};

const mockDestination: Destination = {
  destinationId: "test-destination",
  name: "test destination",
  destinationName: "test destination name",
  workspaceId: "test-workspace-id",
  destinationDefinitionId: "test-destination-definition-id",
  connectionConfiguration: undefined,
};

const mockConnection: Connection = {
  connectionId: "test-connection",
  name: "test connection",
  prefix: "test",
  sourceId: "test-source",
  destinationId: "test-destination",
  status: ConnectionStatus.ACTIVE,
  schedule: null,
  syncCatalog: {
    streams: [],
  },
  namespaceDefinition: ConnectionNamespaceDefinition.Source,
  namespaceFormat: "",
  latestSyncJobStatus: null,
  operationIds: [],
  source: mockSource,
  destination: mockDestination,
  operations: [],
  catalogId: "",
};

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => {
  return {
    useGetDestinationDefinitionSpecification: () => {
      return "destinationDefinition";
    },
  };
});

jest.mock("services/workspaces/WorkspacesService", () => {
  return {
    useCurrentWorkspace: () => {
      return "currentWorkspace";
    },
  };
});

describe("<ConnectionForm />", () => {
  let container: HTMLElement;
  describe("edit mode", () => {
    beforeEach(async () => {
      const renderResult = await render(
        <ConnectionForm onSubmit={jest.fn()} mode="edit" connection={mockConnection} />
      );
      container = renderResult.container;
    });
    test("it renders relevant items", async () => {
      const prefixInput = container.querySelector("div[data-testid='prefixInput']");
      expect(prefixInput).toBeInTheDocument();

      userEvent.type(prefixInput!, "{selectall}{del}prefix");
      await waitFor(() => userEvent.keyboard("{enter}"));
    });
    test("pointer events are not turned off anywhere in the component", async () => {
      expect(container.innerHTML).toContain("checkbox");
    });
  });
  describe("readonly mode", () => {
    beforeEach(async () => {
      const renderResult = await render(
        <ConnectionForm onSubmit={jest.fn()} mode="readonly" connection={mockConnection} />
      );
      container = renderResult.container;
    });
    test("it renders only relevant items for the mode", async () => {
      const prefixInput = container.querySelector("div[data-testid='prefixInput']");
      expect(prefixInput).toBeInTheDocument();
    });
    test("pointer events are turned off in the fieldset", async () => {
      expect(container.innerHTML).not.toContain("checkbox");
    });
  });
});
