/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { act, render, RenderResult } from "@testing-library/react";
import { Suspense } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import { TestWrapper } from "test-utils/testutils";

import { AirbyteCatalog } from "core/request/AirbyteClient";
import { ServicesProvider } from "core/servicesProvider";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureService } from "hooks/services/Feature";
import * as sourceHook from "hooks/services/useSourceHook";
import { ConfigProvider } from "packages/cloud/services/ConfigProvider";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";

import { CreateConnectionForm } from "./CreateConnectionForm";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));

describe("CreateConnectionForm", () => {
  const Wrapper: React.FC = ({ children }) => (
    <Suspense fallback={<div>I should not show up in a snapshot</div>}>
      <TestWrapper>
        <MemoryRouter>
          <ConfigProvider>
            <ServicesProvider>
              <QueryClientProvider client={new QueryClient()}>
                <ConfirmationModalService>
                  <FeatureService features={[]}>
                    <AnalyticsProvider>{children}</AnalyticsProvider>
                  </FeatureService>
                </ConfirmationModalService>
              </QueryClientProvider>
            </ServicesProvider>
          </ConfigProvider>
        </MemoryRouter>
      </TestWrapper>
    </Suspense>
  );

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
