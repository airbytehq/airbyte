/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { act, render as tlr } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import selectEvent from "react-select-event";
import { mockConnection } from "test-utils/mock-data/mockConnection";
import {
  mockDestinationDefinition,
  mockDestinationDefinitionSpecification,
} from "test-utils/mock-data/mockDestination";
import { mockSourceDefinition, mockSourceDefinitionSpecification } from "test-utils/mock-data/mockSource";
import { TestWrapper } from "test-utils/testutils";

import { defaultOssFeatures, FeatureItem } from "hooks/services/Feature";
import * as sourceHook from "hooks/services/useSourceHook";

import { CreateConnectionForm } from "./CreateConnectionForm";

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
  useCurrentWorkspace: () => ({}),
  useCurrentWorkspaceId: () => "workspace-id",
}));

describe("CreateConnectionForm", () => {
  const Wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => <TestWrapper>{children}</TestWrapper>;
  const render = async () => {
    let renderResult: ReturnType<typeof tlr>;

    await act(async () => {
      renderResult = tlr(
        <Wrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </Wrapper>
      );
    });
    return renderResult!;
  };

  const baseUseDiscoverSchema = {
    schemaErrorStatus: null,
    isLoading: false,
    schema: mockConnection.syncCatalog,
    catalogId: "",
    onDiscoverSchema: () => Promise.resolve(),
  };

  it("should render", async () => {
    jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => baseUseDiscoverSchema);
    const renderResult = await render();
    expect(renderResult).toMatchSnapshot();
    expect(renderResult.queryByText("Please wait a little bit more…")).toBeFalsy();
  });

  it("should render when loading", async () => {
    jest
      .spyOn(sourceHook, "useDiscoverSchema")
      .mockImplementationOnce(() => ({ ...baseUseDiscoverSchema, isLoading: true }));

    const renderResult = await render();
    expect(renderResult).toMatchSnapshot();
  });

  it("should render with an error", async () => {
    jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => ({
      ...baseUseDiscoverSchema,
      schemaErrorStatus: new Error("Test Error") as sourceHook.SchemaError,
    }));

    const renderResult = await render();
    expect(renderResult).toMatchSnapshot();
  });

  describe("cron expression validation", () => {
    const INVALID_CRON_EXPRESSION = "invalid cron expression";
    const CRON_EXPRESSION_EVERY_MINUTE = "* * * * * * ?";

    it("should display an error for an invalid cron expression", async () => {
      jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => baseUseDiscoverSchema);

      const container = tlr(
        <TestWrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </TestWrapper>
      );

      await selectEvent.select(container.getByTestId("scheduleData"), /cron/i);

      const cronExpressionInput = container.getByTestId("cronExpression");

      userEvent.clear(cronExpressionInput);
      await userEvent.type(cronExpressionInput, INVALID_CRON_EXPRESSION, { delay: 1 });

      const errorMessage = container.getByText("Invalid cron expression");

      expect(errorMessage).toBeInTheDocument();
    });

    it("should allow cron expressions under one hour when feature enabled", async () => {
      jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => baseUseDiscoverSchema);

      const container = tlr(
        <TestWrapper>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
        </TestWrapper>
      );

      await selectEvent.select(container.getByTestId("scheduleData"), /cron/i);

      const cronExpressionField = container.getByTestId("cronExpression");

      await userEvent.type(cronExpressionField, `{selectall}${CRON_EXPRESSION_EVERY_MINUTE}`, { delay: 1 });

      const errorMessage = container.queryByTestId("cronExpressionError");

      expect(errorMessage).not.toBeInTheDocument();
    });

    it("should not allow cron expressions under one hour when feature not enabled", async () => {
      jest.spyOn(sourceHook, "useDiscoverSchema").mockImplementationOnce(() => baseUseDiscoverSchema);

      const featuresToInject = defaultOssFeatures.filter((f) => f !== FeatureItem.AllowSyncSubOneHourCronExpressions);

      const container = tlr(
        <TestWrapper features={featuresToInject}>
          <CreateConnectionForm source={mockConnection.source} destination={mockConnection.destination} />
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
