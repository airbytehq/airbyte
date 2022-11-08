/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */

import { render as tlr, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React, { Suspense } from "react";
import selectEvent from "react-select-event";
import { mockConnection } from "test-utils/mock-data/mockConnection";
import { mockDestination } from "test-utils/mock-data/mockDestination";
import { mockWorkspace } from "test-utils/mock-data/mockWorkspace";
import { mockWorkspaceId } from "test-utils/mock-data/mockWorkspaceId";
import { TestWrapper } from "test-utils/testutils";

import { WebBackendConnectionUpdate } from "core/request/AirbyteClient";
import { ConnectionEditServiceProvider } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { defaultFeatures, FeatureItem } from "hooks/services/Feature";
import * as connectionHook from "hooks/services/useConnectionHook";

import { ConnectionReplicationTab } from "./ConnectionReplicationTab";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDestination,
}));
jest.setTimeout(10000);

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => mockWorkspace,
  useCurrentWorkspaceId: () => mockWorkspaceId,
}));

describe("ConnectionReplicationTab", () => {
  const Wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
    <Suspense fallback={<div>I should not show up in a snapshot</div>}>
      <TestWrapper>
        <ConnectionEditServiceProvider connectionId={mockConnection.connectionId}>
          {children}
        </ConnectionEditServiceProvider>
      </TestWrapper>
    </Suspense>
  );
  const render = async () => {
    let renderResult: ReturnType<typeof tlr>;
    await act(async () => {
      renderResult = tlr(
        <Wrapper>
          <ConnectionReplicationTab />
        </Wrapper>
      );
    });
    return renderResult!;
  };

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

    const renderResult = await render();
    expect(renderResult).toMatchSnapshot();
  });

  it("should show an error if there is a schemaError", async () => {
    setupSpies(() => Promise.reject("Test Error"));

    const renderResult = await render();

    await act(async () => {
      renderResult.queryByText("Refresh source schema")?.click();
    });
    expect(renderResult).toMatchSnapshot();
  });

  it("should show loading if the schema is refreshing", async () => {
    setupSpies();

    const renderResult = await render();
    await act(async () => {
      renderResult.queryByText("Refresh source schema")?.click();
    });

    await act(async () => {
      expect(renderResult.findByText("We are fetching the schema of your data source.", { exact: false })).toBeTruthy();
    });
  });

  describe("cron expression validation", () => {
    const INVALID_CRON_EXPRESSION = "invalid cron expression";
    const CRON_EXPRESSION_EVERY_MINUTE = "* * * * * * ?";

    it("should display an error for an invalid cron expression", async () => {
      setupSpies();
      const renderResult = await render();

      await selectEvent.select(renderResult.getByTestId("scheduleData"), /cron/i);

      const cronExpressionInput = renderResult.getByTestId("cronExpression");

      userEvent.clear(cronExpressionInput);
      await userEvent.type(cronExpressionInput, INVALID_CRON_EXPRESSION, { delay: 1 });

      const errorMessage = renderResult.getByText("Invalid cron expression");

      expect(errorMessage).toBeInTheDocument();
    });

    it("should allow cron expressions under one hour when feature enabled", async () => {
      setupSpies();

      const renderResult = await render();

      await selectEvent.select(renderResult.getByTestId("scheduleData"), /cron/i);

      const cronExpressionField = renderResult.getByTestId("cronExpression");

      await userEvent.type(cronExpressionField, `{selectall}${CRON_EXPRESSION_EVERY_MINUTE}`, { delay: 1 });

      const errorMessage = renderResult.queryByTestId("cronExpressionError");

      expect(errorMessage).not.toBeInTheDocument();
    });

    it("should not allow cron expressions under one hour when feature not enabled", async () => {
      setupSpies();

      const featuresToInject = defaultFeatures.filter((f) => f !== FeatureItem.AllowSyncSubOneHourCronExpressions);

      const container = tlr(
        <TestWrapper features={featuresToInject}>
          <ConnectionEditServiceProvider connectionId={mockConnection.connectionId}>
            <ConnectionReplicationTab />
          </ConnectionEditServiceProvider>
        </TestWrapper>
      );

      await selectEvent.select(container.getByTestId("scheduleData"), /cron/i);

      const cronExpressionField = container.getByTestId("cronExpression");

      await userEvent.type(cronExpressionField, `{selectall}${CRON_EXPRESSION_EVERY_MINUTE}`, { delay: 1 });

      const errorMessage = container.getByTestId("cronExpressionError");

      expect(errorMessage).toBeInTheDocument();
    });
  });
});
