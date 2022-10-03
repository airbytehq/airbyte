/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */

import { render, act, RenderResult } from "@testing-library/react";
import { Suspense } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionUpdate } from "core/request/AirbyteClient";
import { ServicesProvider } from "core/servicesProvider";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { ConnectionEditServiceProvider } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { ModalServiceProvider } from "hooks/services/Modal";
import { ConfigProvider } from "packages/cloud/services/ConfigProvider";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";

import { ConnectionReplicationTab } from "./ConnectionReplicationTab";

jest.mock("hooks/services/useConnectionHook", () => {
  const useConnHook = jest.requireActual("hooks/services/useConnectionHook");
  let count = 0;
  return {
    ...useConnHook,
    useGetConnection: () => mockConnection,
    useWebConnectionService: () => ({
      getConnection: (() => {
        return () => {
          if (count === 0) {
            count++;
            return Promise.reject("Test Error");
          }
          return new Promise(() => null);
        };
      })(),
    }),
    useUpdateConnection: () => ({
      mutateAsync: jest.fn(async (connection: WebBackendConnectionUpdate) => connection),
      isLoading: false,
    }),
  };
});

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));

// TODO: This component needs more testing but it should be done VIA e2e and integration-style tests.
describe("ConnectionReplicationTab", () => {
  const Wrapper: React.FC = ({ children }) => (
    <Suspense fallback={<div>I should not show up in a snapshot</div>}>
      <TestWrapper>
        <MemoryRouter>
          <ModalServiceProvider>
            <ConfigProvider>
              <ServicesProvider>
                <QueryClientProvider client={new QueryClient()}>
                  <ConfirmationModalService>
                    <ConnectionEditServiceProvider connectionId={mockConnection.connectionId}>
                      <AnalyticsProvider>{children}</AnalyticsProvider>
                    </ConnectionEditServiceProvider>
                  </ConfirmationModalService>
                </QueryClientProvider>
              </ServicesProvider>
            </ConfigProvider>
          </ModalServiceProvider>
        </MemoryRouter>
      </TestWrapper>
    </Suspense>
  );
  it("should render", async () => {
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
