/* eslint-disable @typescript-eslint/no-explicit-any */
import { act } from "@testing-library/react";
import { renderHook } from "@testing-library/react-hooks";
import React from "react";
import { MemoryRouter } from "react-router-dom";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import mockWorkspace from "test-utils/mock-data/mockWorkspace.json";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";

import { ModalCancel } from "../Modal";
import {
  ConnectionFormServiceProvider,
  ConnectionServiceProps,
  useConnectionFormService,
} from "./ConnectionFormService";

["packages/cloud/services/workspaces/WorkspacesService", "services/workspaces/WorkspacesService"].forEach((s) =>
  jest.mock(s, () => ({
    useCurrentWorkspaceId: () => mockWorkspace.workspaceId,
    useCurrentWorkspace: () => mockWorkspace,
  }))
);

jest.mock("../FormChangeTracker", () => ({
  useFormChangeTrackerService: () => ({ clearFormChange: () => null }),
  useUniqueFormId: () => "blah",
}));
jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));

describe("ConnectionFormService", () => {
  const Wrapper: React.FC<ConnectionServiceProps> = ({ children, ...props }) => (
    <TestWrapper>
      <MemoryRouter>
        <ConnectionFormServiceProvider {...props}>{children}</ConnectionFormServiceProvider>
      </MemoryRouter>
    </TestWrapper>
  );

  const onSubmit = jest.fn();
  const onAfterSubmit = jest.fn();
  const onCancel = jest.fn();

  beforeEach(() => {
    onSubmit.mockReset();
    onAfterSubmit.mockReset();
    onCancel.mockReset();
  });

  it("should call onSubmit when submitted", async () => {
    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: mockConnection as WebBackendConnectionRead,
        mode: "create",
        formId: Math.random().toString(),
        onSubmit,
        onAfterSubmit,
        onCancel,
        formDirty: false,
      },
    });

    const resetForm = jest.fn();
    const testValues: any = {};
    await act(async () => {
      await result.current.onFormSubmit(testValues, { resetForm } as any);
    });

    expect(resetForm).toBeCalledWith({ values: testValues });
    expect(onSubmit).toBeCalledWith({
      operations: [],
      scheduleType: "manual",
      syncCatalog: {
        streams: undefined,
      },
    });
    expect(onAfterSubmit).toBeCalledWith();
    expect(result.current.errorMessage).toBe(null);
  });

  it("should catch if onSubmit throws and generate an error message", async () => {
    const errorMessage = "asdf";
    onSubmit.mockImplementation(async () => {
      throw new Error(errorMessage);
    });

    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: mockConnection as WebBackendConnectionRead,
        mode: "create",
        formId: Math.random().toString(),
        onSubmit,
        onAfterSubmit,
        onCancel,
        formDirty: false,
      },
    });

    const resetForm = jest.fn();
    const testValues: any = {};
    await act(async () => {
      await result.current.onFormSubmit(testValues, { resetForm } as any);
    });

    expect(result.current.errorMessage).toBe(errorMessage);
    expect(resetForm).not.toHaveBeenCalled();
  });

  it("should catch if onSubmit throws but not generate an error if it's a ModalCancel error", async () => {
    onSubmit.mockImplementation(async () => {
      throw new ModalCancel();
    });

    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: mockConnection as WebBackendConnectionRead,
        mode: "create",
        formId: Math.random().toString(),
        onSubmit,
        onAfterSubmit,
        onCancel,
        formDirty: false,
      },
    });

    const resetForm = jest.fn();
    const testValues: any = {};
    await act(async () => {
      await result.current.onFormSubmit(testValues, { resetForm } as any);
    });

    expect(result.current.errorMessage).toBe(null);
    expect(resetForm).not.toHaveBeenCalled();
  });

  it("should render the generic form invalid error message if the form is dirty and there has not been a submit error", async () => {
    const { result } = renderHook(useConnectionFormService, {
      wrapper: Wrapper,
      initialProps: {
        connection: mockConnection as WebBackendConnectionRead,
        mode: "create",
        formId: Math.random().toString(),
        onSubmit,
        onAfterSubmit,
        onCancel,
        formDirty: true,
      },
    });

    expect(result.current.errorMessage).toBe("The form is invalid. Please make sure that all fields are correct.");
  });
});
