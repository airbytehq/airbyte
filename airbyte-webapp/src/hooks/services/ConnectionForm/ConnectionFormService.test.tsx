import { act, renderHook } from "@testing-library/react-hooks";
import React from "react";
import { mockConnection } from "test-utils/mock-data/mockConnection";
import {
  mockDestinationDefinition,
  mockDestinationDefinitionSpecification,
} from "test-utils/mock-data/mockDestination";
import { mockSourceDefinition, mockSourceDefinitionSpecification } from "test-utils/mock-data/mockSource";
import { mockWorkspace } from "test-utils/mock-data/mockWorkspace";
import { TestWrapper } from "test-utils/testutils";

import { FormError } from "utils/errorStatusMessage";

import {
  ConnectionFormServiceProvider,
  ConnectionOrPartialConnection,
  useConnectionFormService,
} from "./ConnectionFormService";

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

describe("ConnectionFormService", () => {
  const Wrapper: React.FC<Parameters<typeof ConnectionFormServiceProvider>[0]> = ({ children, ...props }) => (
    <TestWrapper>
      <ConnectionFormServiceProvider {...props}>{children}</ConnectionFormServiceProvider>
    </TestWrapper>
  );

  const refreshSchema = jest.fn();

  beforeEach(() => {
    refreshSchema.mockReset();
  });

  it("should take a partial Connection", async () => {
    const partialConnection: ConnectionOrPartialConnection = {
      syncCatalog: mockConnection.syncCatalog,
      source: mockConnection.source,
      destination: mockConnection.destination,
    };
    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: partialConnection,
        mode: "create",
        refreshSchema,
      },
    });

    expect(result.current.connection).toEqual(partialConnection);
  });

  it("should take a full Connection", async () => {
    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: mockConnection,
        mode: "create",
        refreshSchema,
      },
    });

    expect(result.current.connection).toEqual(mockConnection);
  });

  describe("Error Message Generation", () => {
    it("should show a validation error if the form is invalid and dirty", async () => {
      const { result } = renderHook(useConnectionFormService, {
        wrapper: Wrapper,
        initialProps: {
          connection: mockConnection,
          mode: "create",
          refreshSchema,
        },
      });

      expect(result.current.getErrorMessage(false, true)).toBe(
        "The form is invalid. Please make sure that all fields are correct."
      );
    });

    it("should not show a validation error if the form is valid and dirty", async () => {
      const { result } = renderHook(useConnectionFormService, {
        wrapper: Wrapper,
        initialProps: {
          connection: mockConnection,
          mode: "create",
          refreshSchema,
        },
      });

      expect(result.current.getErrorMessage(true, true)).toBe(null);
    });

    it("should not show a validation error if the form is invalid and not dirty", async () => {
      const { result } = renderHook(useConnectionFormService, {
        wrapper: Wrapper,
        initialProps: {
          connection: mockConnection,
          mode: "create",
          refreshSchema,
        },
      });

      expect(result.current.getErrorMessage(false, false)).toBe(null);
    });

    it("should show a message when given a submit error", () => {
      const { result } = renderHook(useConnectionFormService, {
        wrapper: Wrapper,
        initialProps: {
          connection: mockConnection,
          mode: "create",
          refreshSchema,
        },
      });

      const errMsg = "asdf";
      act(() => {
        result.current.setSubmitError(new FormError(errMsg));
      });

      expect(result.current.getErrorMessage(false, false)).toBe(errMsg);
      expect(result.current.getErrorMessage(false, true)).toBe(errMsg);
      expect(result.current.getErrorMessage(true, false)).toBe(errMsg);
      expect(result.current.getErrorMessage(true, true)).toBe(errMsg);
    });
  });
});
