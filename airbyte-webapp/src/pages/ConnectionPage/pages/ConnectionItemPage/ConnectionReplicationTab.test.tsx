/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */

import { render, act, RenderResult } from "@testing-library/react";
import { Suspense } from "react";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionUpdate } from "core/request/AirbyteClient";
import { ConnectionEditServiceProvider } from "hooks/services/ConnectionEdit/ConnectionEditService";
import * as connectionHook from "hooks/services/useConnectionHook";

import { ConnectionReplicationTab } from "./ConnectionReplicationTab";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));

// TODO: This component needs more testing but it should be done VIA e2e and integration-style tests.
describe("ConnectionReplicationTab", () => {
  const Wrapper: React.FC = ({ children }) => (
    <Suspense fallback={<div>I should not show up in a snapshot</div>}>
      <TestWrapper>
        <ConnectionEditServiceProvider connectionId={mockConnection.connectionId}>
          {children}
        </ConnectionEditServiceProvider>
      </TestWrapper>
    </Suspense>
  );

  const setupSpies = (getConnection?: () => Promise<void>) => {
    const getConnectionImpl: any = {
      getConnection: getConnection ?? (() => new Promise(() => null) as any),
    };
    jest.spyOn(connectionHook, "useGetConnection").mockImplementation(() => mockConnection as any);
    jest.spyOn(connectionHook, "useWebConnectionService").mockImplementation(() => getConnectionImpl);
    jest.spyOn(connectionHook, "useUpdateConnection").mockImplementation(
      () =>
        ({
          mutateAsync: async (connection: WebBackendConnectionUpdate) => connection,
          isLoading: false,
        } as any)
    );
  };
  it("should render", async () => {
    setupSpies();

    let renderResult: RenderResult;
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <ConnectionReplicationTab />
        </Wrapper>
      );
    });
    expect(renderResult!.container).toMatchSnapshot();
  });

  it("should show an error if there is a schemaError", async () => {
    setupSpies(() => Promise.reject("Test Error"));

    let renderResult: RenderResult;
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <ConnectionReplicationTab />
        </Wrapper>
      );
    });

    await act(async () => {
      renderResult!.queryByText("Refresh source schema")?.click();
    });
    expect(renderResult!.container).toMatchSnapshot();
  });

  it("should show loading if the schema is refreshing", async () => {
    setupSpies();

    let renderResult: RenderResult;
    await act(async () => {
      renderResult = render(
        <Wrapper>
          <ConnectionReplicationTab />
        </Wrapper>
      );
    });

    await act(async () => {
      renderResult!.queryByText("Refresh source schema")?.click();
    });

    await act(async () => {
      expect(
        renderResult!.findByText("We are fetching the schema of your data source.", { exact: false })
      ).toBeTruthy();
    });
  });
});
