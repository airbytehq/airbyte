import { act, Queries, queries, render as rtlRender, RenderOptions, RenderResult } from "@testing-library/react";
import React, { Suspense } from "react";
import { IntlProvider } from "react-intl";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ConfigContext, config } from "config";
import {
  ConnectionStatus,
  DestinationRead,
  NamespaceDefinitionType,
  SourceRead,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { ServicesProvider } from "core/servicesProvider";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { defaultOssFeatures, FeatureItem, FeatureService } from "hooks/services/Feature";
import { ModalServiceProvider } from "hooks/services/Modal";
import { NotificationService } from "hooks/services/Notification";
import en from "locales/en.json";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";

interface WrapperProps {
  children?: React.ReactElement;
}

export async function render<
  Q extends Queries = typeof queries,
  Container extends Element | DocumentFragment = HTMLElement
>(ui: React.ReactNode, renderOptions?: RenderOptions<Q, Container>): Promise<RenderResult<Q, Container>> {
  const Wrapper = ({ children }: WrapperProps) => {
    return (
      <TestWrapper>
        <Suspense fallback={<div>testutils render fallback content</div>}>{children}</Suspense>
      </TestWrapper>
    );
  };

  let renderResult: RenderResult<Q, Container>;
  await act(async () => {
    renderResult = rtlRender<Q, Container>(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
  });

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  return renderResult!;
}

interface TestWrapperOptions {
  features?: FeatureItem[];
}
export const TestWrapper: React.FC<React.PropsWithChildren<TestWrapperOptions>> = ({
  children,
  features = defaultOssFeatures,
}) => (
  <ThemeProvider theme={{}}>
    <IntlProvider locale="en" messages={en} onError={() => null}>
      <ConfigContext.Provider value={{ config }}>
        <AnalyticsProvider>
          <NotificationService>
            <FeatureService features={features}>
              <ServicesProvider>
                <ModalServiceProvider>
                  <ConfirmationModalService>
                    <QueryClientProvider client={new QueryClient()}>
                      <MemoryRouter>{children}</MemoryRouter>
                    </QueryClientProvider>
                  </ConfirmationModalService>
                </ModalServiceProvider>
              </ServicesProvider>
            </FeatureService>
          </NotificationService>
        </AnalyticsProvider>
      </ConfigContext.Provider>
    </IntlProvider>
  </ThemeProvider>
);

export const useMockIntersectionObserver = () => {
  // IntersectionObserver isn't available in test environment but is used by the dialog component
  const mockIntersectionObserver = jest.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: jest.fn().mockReturnValue(null),
    unobserve: jest.fn().mockReturnValue(null),
    disconnect: jest.fn().mockReturnValue(null),
  });
  window.IntersectionObserver = mockIntersectionObserver;
};

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
  schemaChange: "no_change",
  notifySchemaChanges: true,
  nonBreakingChangesPreference: "ignore",
};
