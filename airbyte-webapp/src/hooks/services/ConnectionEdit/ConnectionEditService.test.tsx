import { act, renderHook } from "@testing-library/react-hooks";
import React from "react";
import { mockConnection } from "test-utils/mock-data/mockConnection";
import { mockDestination } from "test-utils/mock-data/mockDestination";
import { mockWorkspace } from "test-utils/mock-data/mockWorkspace";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionUpdate } from "core/request/AirbyteClient";

import { useConnectionFormService } from "../ConnectionForm/ConnectionFormService";
import { ConnectionEditServiceProvider, useConnectionEditService } from "./ConnectionEditService";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDestination,
}));

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => mockWorkspace,
}));

jest.mock("../useConnectionHook", () => ({
  useGetConnection: () => mockConnection,
  useWebConnectionService: () => ({
    getConnection: () => mockConnection,
  }),
  useUpdateConnection: () => ({
    mutateAsync: jest.fn(async (connection: WebBackendConnectionUpdate) => {
      return { ...mockConnection, ...connection };
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

  it("should refresh connection", async () => {
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
    expect(result.current[0].connection).toEqual(mockConnection);
  });

  it("should refresh connection only if the catalog has changed", async () => {
    // Need to combine the hooks so both can be used.
    const useMyTestHook = () =>
      ({ editService: useConnectionEditService(), formService: useConnectionFormService() } as const);

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
    };

    await act(async () => {
      await result.current.editService.updateConnection(mockUpdateConnection);
    });

    expect(result.current.editService.connection).toEqual({ ...mockConnection, ...mockUpdateConnection });

    await act(async () => {
      await result.current.formService.refreshSchema();
    });

    expect(result.current.editService.schemaHasBeenRefreshed).toBe(false);
    expect(result.current.editService.schemaRefreshing).toBe(false);
    expect(result.current.editService.connection).toEqual(mockConnection);
  });

  it("should clear the refreshed schema", async () => {
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
      syncCatalog: { streams: [] },
    };

    const updatedConnection = { ...mockConnection, ...connectionUpdate };

    await act(async () => {
      // Update the connection to verify that it has been cleared later
      await result.current.editService.updateConnection(connectionUpdate);

      await result.current.formService.refreshSchema();
      result.current.editService.clearRefreshedSchema();
    });

    expect(result.current.editService.schemaHasBeenRefreshed).toBe(false);
    expect(result.current.editService.schemaRefreshing).toBe(false);
    expect(result.current.editService.connection).toEqual(updatedConnection);
  });
});
