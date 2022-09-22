import { waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "test-utils/testutils";

import {
  ConnectionStatus,
  DestinationRead,
  NamespaceDefinitionType,
  SourceRead,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal/ConfirmationModalService";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";

import { ConnectionForm, ConnectionFormMode } from "./ConnectionForm";

const mockSource: SourceRead = {
  sourceId: "test-source",
  name: "test source",
  sourceName: "test-source-name",
  workspaceId: "test-workspace-id",
  sourceDefinitionId: "test-source-definition-id",
  connectionConfiguration: undefined,
};

const mockDestination: DestinationRead = {
  destinationId: "test-destination",
  name: "test destination",
  destinationName: "test destination name",
  workspaceId: "test-workspace-id",
  destinationDefinitionId: "test-destination-definition-id",
  connectionConfiguration: undefined,
};

const mockConnection: WebBackendConnectionRead = {
  connectionId: "test-connection",
  name: "test connection",
  prefix: "test",
  sourceId: "test-source",
  destinationId: "test-destination",
  status: ConnectionStatus.active,
  scheduleType: "manual",
  scheduleData: undefined,
  syncCatalog: {
    streams: [],
  },
  namespaceDefinition: NamespaceDefinitionType.source,
  namespaceFormat: "",
  operationIds: [],
  source: mockSource,
  destination: mockDestination,
  operations: [],
  catalogId: "",
  isSyncing: false,
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
    useCurrentWorkspaceId: () => {
      return "currentWorkspace";
    },
  };
});

const renderConnectionForm = (mode: ConnectionFormMode, connection = mockConnection) =>
  render(
    <ConfirmationModalService>
      <ConnectionFormServiceProvider
        mode={mode}
        connection={connection}
        formId={Math.random().toString()}
        onSubmit={jest.fn()}
        formDirty={false}
      >
        <ConnectionForm />
      </ConnectionFormServiceProvider>
    </ConfirmationModalService>
  );

describe("<ConnectionForm />", () => {
  let container: HTMLElement;
  describe("edit mode", () => {
    beforeEach(async () => {
      const renderResult = await renderConnectionForm("edit");

      container = renderResult.container;
    });
    it("renders relevant items", async () => {
      const prefixInput = container.querySelector("input[data-testid='prefixInput']");
      expect(prefixInput).toBeInTheDocument();

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      userEvent.type(prefixInput!, "{selectall}{del}prefix");
      await waitFor(() => userEvent.keyboard("{enter}"));
    });
    it("pointer events are not turned off anywhere in the component", async () => {
      expect(container.innerHTML).toContain("checkbox");
    });
  });
  describe("readonly mode", () => {
    beforeEach(async () => {
      const renderResult = await renderConnectionForm("readonly");

      container = renderResult.container;
    });
    it("renders only relevant items for the mode", async () => {
      const prefixInput = container.querySelector("input[data-testid='prefixInput']");
      expect(prefixInput).toBeInTheDocument();
    });
    it("pointer events are turned off in the fieldset", async () => {
      expect(container.innerHTML).not.toContain("checkbox");
    });
  });
});
