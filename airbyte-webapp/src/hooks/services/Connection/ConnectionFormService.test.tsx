/* eslint-disable @typescript-eslint/no-explicit-any */
import { act } from "@testing-library/react";
import { renderHook } from "@testing-library/react-hooks";
import React from "react";
import { MemoryRouter } from "react-router-dom";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { TestWrapper } from "utils/testutils";

import { ModalCancel } from "../Modal";
import {
  ConnectionFormServiceProvider,
  ConnectionServiceProps,
  useConnectionFormService,
} from "./ConnectionFormService";
import mockConnection from "./mockConnection.json";
import mockDest from "./mockDestinationDefinition.json";

const mockWorkspace = {
  workspaceId: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  customerId: "55dd55e2-33ac-44dc-8d65-5aa7c8624f72",
  email: "krishna@airbyte.com",
  name: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  slug: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  initialSetupComplete: true,
  displaySetupWizard: false,
  anonymousDataCollection: false,
  news: false,
  securityUpdates: false,
  notifications: [],
};

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
        onSubmit,
        onAfterSubmit,
        onCancel,
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
      scheduleData: {
        basicSchedule: {
          timeUnit: undefined,
          units: undefined,
        },
      },
      scheduleType: "manual",
      syncCatalog: {
        streams: undefined,
      },
    });
    expect(onAfterSubmit).toBeCalledWith();
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
        onSubmit,
        onAfterSubmit,
        onCancel,
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
        onSubmit,
        onAfterSubmit,
        onCancel,
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
});
