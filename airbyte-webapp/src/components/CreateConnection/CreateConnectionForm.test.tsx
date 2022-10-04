/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { act, render, RenderResult } from "@testing-library/react";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import { TestWrapper } from "test-utils/testutils";

import { AirbyteCatalog } from "core/request/AirbyteClient";
import * as sourceHook from "hooks/services/useSourceHook";

import { CreateConnectionForm } from "./CreateConnectionForm";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => ({}),
  useCurrentWorkspaceId: () => "workspace-id",
}));

describe("CreateConnectionForm", () => {
  const Wrapper: React.FC = ({ children }) => <TestWrapper>{children}</TestWrapper>;

  const baseUseDiscoverSchema = {
    schemaErrorStatus: null,
    isLoading: false,
    schema: mockConnection.syncCatalog as AirbyteCatalog,
    catalogId: "",
    onDiscoverSchema: () => Promise.resolve(),
  };

  it("should render", async () => {
    let renderResult: RenderResult;
    jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => baseUseDiscoverSchema);
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </Wrapper>
      );
    });
    expect(renderResult!.container).toMatchSnapshot();
    expect(renderResult!.queryByText("Please wait a little bit more…")).toBeFalsy();
  });

  it("should render when loading", async () => {
    let renderResult: RenderResult;
    jest
      .spyOn(sourceHook, "useDiscoverSchema")
      .mockImplementationOnce(() => ({ ...baseUseDiscoverSchema, isLoading: true }));
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </Wrapper>
      );
    });
    expect(renderResult!.container).toMatchSnapshot();
  });

  it("should render with an error", async () => {
    let renderResult: RenderResult;
    jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => ({
      ...baseUseDiscoverSchema,
      schemaErrorStatus: new Error("Test Error") as sourceHook.SchemaError,
    }));
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </Wrapper>
      );
    });
    expect(renderResult!.container).toMatchSnapshot();
  });
});
