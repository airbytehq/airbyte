import { render } from "@testing-library/react";
import { mockDestinationDefinition } from "test-utils/mock-data/mockDestination";
import { mockSourceDefinition } from "test-utils/mock-data/mockSource";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { ConnectionStatus, SchemaChange } from "core/request/AirbyteClient";
import { defaultOssFeatures, FeatureItem } from "hooks/services/Feature";

// eslint-disable-next-line css-modules/no-unused-class
import styles from "./ConnectionInfoCard.module.scss";

const mockUseConnectionEditService = jest.fn();

jest.doMock("hooks/services/ConnectionEdit/ConnectionEditService", () => ({
  useConnectionEditService: mockUseConnectionEditService,
}));

jest.doMock("hooks/services/ConnectionForm/ConnectionFormService.tsx", () => ({
  useConnectionFormService: () => ({
    sourceDefinition: mockSourceDefinition,
    destDefinition: mockDestinationDefinition,
  }),
}));

jest.doMock("components/connection/ConnectionForm/refreshSourceSchemaWithConfirmationOnDirty", () => ({
  useRefreshSourceSchemaWithConfirmationOnDirty: jest.fn(),
}));

const TestWrapperWithAutoDetectSchema: React.FC<React.PropsWithChildren<Record<string, unknown>>> = ({ children }) => (
  <TestWrapper features={[...defaultOssFeatures, FeatureItem.AllowAutoDetectSchema]}>{children}</TestWrapper>
);

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { ConnectionInfoCard } = require("./ConnectionInfoCard");

describe(`<${ConnectionInfoCard.name} />`, () => {
  beforeEach(() => {
    mockUseConnectionEditService.mockReturnValue({
      connection: mockConnection,
      schemaHasBeenRefreshed: false,
    });
  });

  it("renders", () => {
    const { getByTestId, queryByTestId } = render(<ConnectionInfoCard />, { wrapper: TestWrapperWithAutoDetectSchema });

    expect(getByTestId("connectionInfo")).toBeDefined();

    expect(getByTestId("enabledControl")).toBeDefined();
    expect(getByTestId("enabledControl-switch")).toBeEnabled();

    // schema changes-related
    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);
    expect(queryByTestId("schemaChangesDetected")).toBeFalsy();
  });

  it("renders controls features when readonly", () => {
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, status: ConnectionStatus.deprecated, schemaChange: SchemaChange.breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId, queryByTestId } = render(<ConnectionInfoCard />, { wrapper: TestWrapperWithAutoDetectSchema });

    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);

    expect(queryByTestId("enabledControl")).toBeFalsy();
    expect(queryByTestId("schemaChangesDetected")).toBeFalsy();
  });

  it("renders with breaking schema changes", () => {
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, schemaChange: SchemaChange.breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId } = render(<ConnectionInfoCard />, { wrapper: TestWrapperWithAutoDetectSchema });

    expect(getByTestId("connectionInfo-sourceLink")).toHaveClass(styles.breaking);
    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeDisabled();
  });

  it("renders with non-breaking schema changes", () => {
    mockUseConnectionEditService.mockReturnValueOnce({
      connection: { ...mockConnection, schemaChange: SchemaChange.non_breaking },
      schemaHasBeenRefreshed: false,
    });

    const { getByTestId } = render(<ConnectionInfoCard />, { wrapper: TestWrapperWithAutoDetectSchema });

    expect(getByTestId("connectionInfo-sourceLink")).not.toHaveClass(styles.breaking);
    expect(getByTestId("connectionInfo-sourceLink")).toHaveClass(styles.nonBreaking);
    expect(getByTestId("schemaChangesDetected")).toBeDefined();

    expect(getByTestId("enabledControl-switch")).toBeEnabled();
  });
});
