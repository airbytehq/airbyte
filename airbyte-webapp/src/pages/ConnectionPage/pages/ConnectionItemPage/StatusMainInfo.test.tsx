import { render } from "@testing-library/react";
import { mockDestinationDefinition } from "test-utils/mock-data/mockDestinationDefinition";
import { mockSourceDefinition } from "test-utils/mock-data/mockSourceDefinition";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { ConnectionStatus } from "core/request/AirbyteClient";
import type { useSchemaChanges } from "hooks/connection/useSchemaChanges";

import styles from "./StatusMainInfo.module.scss";

const mockUseConnectionEditService = jest.fn();

jest.doMock("hooks/services/ConnectionEdit/ConnectionEditService", () => ({
  useConnectionEditService: mockUseConnectionEditService,
}));

jest.doMock("services/connector/SourceDefinitionService", () => ({
  useSourceDefinition: () => mockSourceDefinition,
}));

jest.doMock("services/connector/DestinationDefinitionService", () => ({
  useDestinationDefinition: () => mockDestinationDefinition,
}));

const mockUseSchemaChanges = jest.fn<ReturnType<typeof useSchemaChanges>, Parameters<typeof useSchemaChanges>>();

jest.doMock("hooks/connection/useSchemaChanges", () => ({
  useSchemaChanges: mockUseSchemaChanges,
}));

jest.doMock("views/Connection/ConnectionForm/components/refreshSourceSchemaWithConfirmationOnDirty", () => ({
  useRefreshSourceSchemaWithConfirmationOnDirty: jest.fn(),
}));

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { StatusMainInfo } = require("./StatusMainInfo");

describe("<StatusMainInfo />", () => {
  beforeEach(() => {
    mockUseConnectionEditService.mockReturnValue({
      connection: mockConnection,
      schemaHasBeenRefreshed: false,
    });

    mockUseSchemaChanges.mockReturnValue({
      schemaChange: "no_change",
      hasSchemaChanges: false,
      hasBreakingSchemaChange: false,
      hasNonBreakingSchemaChange: false,
    });
  });

  it("renders", () => {
    const { getByTestId, queryByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo")).toBeDefined();

    expect(getByTestId("enabledControl")).toBeDefined();
    expect(getByTestId("enabledControl-switch")).toBeEnabled();

    // schema changes-related
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);
    expect(queryByTestId("schemaChangesDetected")).toBeFalsy();
  });

  it("renders controls features when readonly", () => {
    mockUseSchemaChanges.mockReturnValueOnce({
      schemaChange: "no_change",
      hasSchemaChanges: true,
      hasBreakingSchemaChange: true,
      hasNonBreakingSchemaChange: false,
    });

    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, status: ConnectionStatus.deprecated },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId, queryByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);

    expect(queryByTestId("enabledControl")).toBeFalsy();
    expect(queryByTestId("schemaChangesDetected")).toBeFalsy();
  });

  it("renders with breaking schema changes", () => {
    mockUseSchemaChanges.mockReturnValueOnce({
      schemaChange: "no_change",
      hasSchemaChanges: true,
      hasBreakingSchemaChange: true,
      hasNonBreakingSchemaChange: false,
    });

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeDisabled();
  });

  it("renders with non-breaking schema changes", () => {
    mockUseSchemaChanges.mockReturnValueOnce({
      schemaChange: "no_change",
      hasSchemaChanges: true,
      hasBreakingSchemaChange: false,
      hasNonBreakingSchemaChange: true,
    });

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeEnabled();
  });
});
