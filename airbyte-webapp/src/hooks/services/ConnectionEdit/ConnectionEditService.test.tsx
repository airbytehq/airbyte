import { act, renderHook } from "@testing-library/react-hooks";
import React from "react";
import { mockCatalogDiff } from "test-utils/mock-data/mockCatalogDiff";
import { mockConnection } from "test-utils/mock-data/mockConnection";
import {
  mockDestinationDefinition,
  mockDestinationDefinitionSpecification,
} from "test-utils/mock-data/mockDestination";
import { mockSourceDefinition, mockSourceDefinitionSpecification } from "test-utils/mock-data/mockSource";
import { mockWorkspace } from "test-utils/mock-data/mockWorkspace";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionRead, WebBackendConnectionUpdate } from "core/request/AirbyteClient";

import { ConnectionEditServiceProvider, useConnectionEditService } from "./ConnectionEditService";
import { useConnectionFormService } from "../ConnectionForm/ConnectionFormService";

jest.mock("services/connector/SourceDefinitionService", () => ({
  useSourceDefinition: () => mockSourceDefinition,
}));

jest.mock("services/connector/SourceDefinitionSpecificationService", () => ({
  useGetSourceDefinitionSpecification: () => mockSourceDefinitionSpecification,
}));

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDestinationDefinitionSpecification,
}));

jest.mock("services/connector/DestinationDefinitionService", () => ({
  useDestinationDefinition: () => mockDestinationDefinition,
}));

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => mockWorkspace,
}));

const utils = {
  getMockConnectionWithRefreshedCatalog: (): WebBackendConnectionRead => ({
    ...mockConnection,
    catalogDiff: mockCatalogDiff,
    catalogId: `${mockConnection.catalogId}1`,
  }),
};

jest.mock("../useConnectionHook", () => ({
  useGetConnection: () => mockConnection,
  useWebConnectionService: () => ({
    getConnection: (_connectionId: string, withRefreshedCatalog?: boolean) =>
      withRefreshedCatalog ? utils.getMockConnectionWithRefreshedCatalog() : mockConnection,
  }),
  useUpdateConnection: () => ({
    mutateAsync: jest.fn(async (connection: WebBackendConnectionUpdate) => {
      const { sourceCatalogId, ...connectionUpdate } = connection;
      return { ...mockConnection, ...connectionUpdate, catalogId: sourceCatalogId ?? mockConnection.catalogId };
    }),
    isLoading: false,
  }),
}));

describe("ConnectionEditService", () => {
  const Wrapper: React.FC<Parameters<typeof ConnectionEditServiceProvider>[0]> = ({ children, ...props }) => (
    <TestWrapper>
      <ConnectionEditServiceProvider {...props}>{children}</ConnectionEditServiceProvider>
    </TestWrapper>
  );

  const refreshSchema = jest.fn();

  beforeEach(() => {
    refreshSchema.mockReset();
  });

  it("should load a Connection from a connectionId", async () => {
    const { result } = renderHook(useConnectionEditService, {
      wrapper: Wrapper,
      initialProps: {
        connectionId: mockConnection.connectionId,
      },
    });

    expect(result.current.connection).toEqual(mockConnection);
  });

  it("should update a connection and set the current connection object to the updated connection", async () => {
    const { result } = renderHook(useConnectionEditService, {
      wrapper: Wrapper,
      initialProps: {
        connectionId: mockConnection.connectionId,
      },
    });

    const mockUpdateConnection: WebBackendConnectionUpdate = {
      connectionId: mockConnection.connectionId,
      name: "new connection name",
      prefix: "new connection prefix",
      syncCatalog: { streams: [] },
    };

    await act(async () => {
      await result.current.updateConnection(mockUpdateConnection);
    });

    expect(result.current.connection).toEqual({ ...mockConnection, ...mockUpdateConnection });
  });

  it("should refresh schema", async () => {
    // Need to combine the hooks so both can be used.
    const useMyTestHook = () => {
      return [useConnectionEditService(), useConnectionFormService()] as const;
    };

    const { result } = renderHook(useMyTestHook, {
      wrapper: Wrapper,
      initialProps: {
        connectionId: mockConnection.connectionId,
      },
    });

    const mockUpdateConnection: WebBackendConnectionUpdate = {
      connectionId: mockConnection.connectionId,
      name: "new connection name",
      prefix: "new connection prefix",
      syncCatalog: { streams: [] },
    };

    await act(async () => {
      await result.current[0].updateConnection(mockUpdateConnection);
    });

    expect(result.current[0].connection).toEqual({ ...mockConnection, ...mockUpdateConnection });

    await act(async () => {
      await result.current[1].refreshSchema();
    });

    expect(result.current[0].schemaHasBeenRefreshed).toBe(true);
    expect(result.current[0].schemaRefreshing).toBe(false);
    expect(result.current[0].connection).toEqual(utils.getMockConnectionWithRefreshedCatalog());
  });

  it("should refresh schema only if the sync catalog has diffs", async () => {
    // Need to combine the hooks so both can be used.
    const useMyTestHook = () =>
      ({ editService: useConnectionEditService(), formService: useConnectionFormService() } as const);

    const { result } = renderHook(useMyTestHook, {
      wrapper: Wrapper,
      initialProps: {
        connectionId: mockConnection.connectionId,
      },
    });

    const connectionUpdate = {
      connectionId: mockConnection.connectionId,
      name: "new connection name",
      prefix: "new connection prefix",
    };

    const updatedConnection: WebBackendConnectionRead = {
      ...mockConnection,
      ...connectionUpdate,
    };

    jest.spyOn(utils, "getMockConnectionWithRefreshedCatalog").mockImplementationOnce(
      (): WebBackendConnectionRead => ({
        ...updatedConnection,
        catalogDiff: { transforms: [] },
      })
    );

    await act(async () => {
      await result.current.editService.updateConnection(connectionUpdate);
      await result.current.formService.refreshSchema();
    });

    expect(result.current.editService.schemaHasBeenRefreshed).toBe(false);
    expect(result.current.editService.schemaRefreshing).toBe(false);
    expect(result.current.editService.connection).toEqual(updatedConnection);
  });

  it("should discard the refreshed schema", async () => {
    const useMyTestHook = () =>
      ({ editService: useConnectionEditService(), formService: useConnectionFormService() } as const);

    const { result } = renderHook(useMyTestHook, {
      wrapper: Wrapper,
      initialProps: {
        connectionId: mockConnection.connectionId,
      },
    });

    const connectionUpdate: WebBackendConnectionUpdate = {
      connectionId: mockConnection.connectionId,
      name: "new connection name",
      prefix: "new connection prefix",
    };

    const updatedConnection = { ...mockConnection, ...connectionUpdate };

    await act(async () => {
      await result.current.formService.refreshSchema();
      await result.current.editService.updateConnection(connectionUpdate);
      result.current.editService.discardRefreshedSchema();
    });

    expect(result.current.editService.schemaHasBeenRefreshed).toBe(false);
    expect(result.current.editService.schemaRefreshing).toBe(false);
    expect(result.current.editService.connection).toEqual(updatedConnection);
  });
});
