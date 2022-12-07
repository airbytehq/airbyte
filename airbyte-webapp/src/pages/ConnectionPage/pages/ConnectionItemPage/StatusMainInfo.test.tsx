import { render } from "@testing-library/react";
import { mockDestinationDefinition } from "test-utils/mock-data/mockDestinationDefinition";
import { mockSourceDefinition } from "test-utils/mock-data/mockSourceDefinition";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { ConnectionStatus, SchemaChange } from "core/request/AirbyteClient";

// eslint-disable-next-line css-modules/no-unused-class
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

jest.doMock("views/Connection/ConnectionForm/components/refreshSourceSchemaWithConfirmationOnDirty", () => ({
  useRefreshSourceSchemaWithConfirmationOnDirty: jest.fn(),
}));

jest.mock("hooks/connection/useIsAutoDetectSchemaChangesEnabled", () => ({
  useIsAutoDetectSchemaChangesEnabled: () => true,
}));

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { StatusMainInfo } = require("./StatusMainInfo");

describe("<StatusMainInfo />", () => {
  beforeEach(() => {
    mockUseConnectionEditService.mockReturnValue({
      connection: mockConnection,
      schemaHasBeenRefreshed: false,
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
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, status: ConnectionStatus.deprecated, schemaChange: SchemaChange.breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId, queryByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);

    expect(queryByTestId("enabledControl")).toBeFalsy();
    expect(queryByTestId("schemaChangesDetected")).toBeFalsy();
  });

  it("renders with breaking schema changes", () => {
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, schemaChange: SchemaChange.breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeDisabled();
  });

  it("renders with non-breaking schema changes", () => {
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, schemaChange: SchemaChange.non_breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapper });

    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeEnabled();
  });
});
