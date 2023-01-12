import { render } from "@testing-library/react";
import { mockDestinationDefinitionSpecification } from "test-utils/mock-data/mockDestinationDefinitionSpecification";
import { mockSourceDefinition } from "test-utils/mock-data/mockSourceDefinition";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { ConnectionStatus, SchemaChange } from "core/request/AirbyteClient";
import { defaultOssFeatures, FeatureItem } from "hooks/services/Feature";

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
  useDestinationDefinition: () => mockDestinationDefinitionSpecification,
}));

jest.doMock("views/Connection/ConnectionForm/components/refreshSourceSchemaWithConfirmationOnDirty", () => ({
  useRefreshSourceSchemaWithConfirmationOnDirty: jest.fn(),
}));

const TestWrapperWithAutoDetectSchema: React.FC<React.PropsWithChildren<Record<string, unknown>>> = ({ children }) => (
  <TestWrapper features={[...defaultOssFeatures, FeatureItem.AllowAutoDetectSchema]}>{children}</TestWrapper>
);

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
    const { getByTestId, queryByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapperWithAutoDetectSchema });

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

    const { getByTestId, queryByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapperWithAutoDetectSchema });

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

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapperWithAutoDetectSchema });

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

    const { getByTestId } = render(<StatusMainInfo />, { wrapper: TestWrapperWithAutoDetectSchema });

    expect(getByTestId("statusMainInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("statusMainInfo-sourceLink")).toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeEnabled();
  });
});
