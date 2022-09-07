import { act, Queries, queries, render as rtlRender, RenderOptions, RenderResult } from "@testing-library/react";
import React, { Suspense } from "react";
import { IntlProvider } from "react-intl";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ConfigContext, defaultConfig } from "config";
import {
  ConnectionStatus,
  DestinationRead,
  NamespaceDefinitionType,
  SourceRead,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { ServicesProvider } from "core/servicesProvider";
import { defaultFeatures, FeatureService } from "hooks/services/Feature";
import en from "locales/en.json";

interface WrapperProps {
  children?: React.ReactElement;
}

export async function render<
  Q extends Queries = typeof queries,
  Container extends Element | DocumentFragment = HTMLElement
>(ui: React.ReactNode, renderOptions?: RenderOptions<Q, Container>): Promise<RenderResult<Q, Container>> {
  const Wrapper = ({ children }: WrapperProps) => {
    const queryClient = new QueryClient();

    return (
      <TestWrapper>
        <ConfigContext.Provider value={{ config: defaultConfig }}>
          <FeatureService features={defaultFeatures}>
            <ServicesProvider>
              <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                  <Suspense fallback={<div>'fallback content'</div>}>{children}</Suspense>
                </MemoryRouter>
              </QueryClientProvider>
            </ServicesProvider>
          </FeatureService>
        </ConfigContext.Provider>
      </TestWrapper>
    );
  };

  let renderResult: RenderResult<Q, Container>;
  await act(async () => {
    renderResult = await rtlRender<Q, Container>(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
  });

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  return renderResult!;
}
export const TestWrapper: React.FC = ({ children }) => (
  <ThemeProvider theme={{}}>
    <IntlProvider locale="en" messages={en} onError={() => null}>
      {children}
    </IntlProvider>
  </ThemeProvider>
);

export const mockSource: SourceRead = {
  sourceId: "test-source",
  name: "test source",
  sourceName: "test-source-name",
  workspaceId: "test-workspace-id",
  sourceDefinitionId: "test-source-definition-id",
  connectionConfiguration: undefined,
};

export const mockDestination: DestinationRead = {
  destinationId: "test-destination",
  name: "test destination",
  destinationName: "test destination name",
  workspaceId: "test-workspace-id",
  destinationDefinitionId: "test-destination-definition-id",
  connectionConfiguration: undefined,
};

export const mockConnection: WebBackendConnectionRead = {
  connectionId: "test-connection",
  name: "test connection",
  prefix: "test",
  sourceId: "test-source",
  destinationId: "test-destination",
  status: ConnectionStatus.active,
  schedule: undefined,
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
