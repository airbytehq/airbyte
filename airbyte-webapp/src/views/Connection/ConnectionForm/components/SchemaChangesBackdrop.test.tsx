import { render } from "@testing-library/react";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem } from "hooks/services/Feature";
const mockUseConnectionEditService = jest.fn();

jest.doMock("hooks/services/ConnectionEdit/ConnectionEditService", () => ({
  useConnectionEditService: mockUseConnectionEditService,
}));

const TestWrapperWithAutoDetectSchema: React.FC<React.PropsWithChildren<Record<string, unknown>>> = ({ children }) => (
  <TestWrapper features={[FeatureItem.AllowAutoDetectSchemaChanges]}>{children}</TestWrapper>
);

const renderComponent = () =>
  render(
    <SchemaChangeBackdrop>
      <button>don't click</button>
    </SchemaChangeBackdrop>,
    { wrapper: TestWrapperWithAutoDetectSchema }
  );

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { SchemaChangeBackdrop } = require("./SchemaChangeBackdrop");

describe("SchemaChangesBackdrop", () => {
  it("renders with breaking changes", () => {
    mockUseConnectionEditService.mockReturnValue({
      connection: { mockConnection, schemaChange: SchemaChange.breaking },
      schemaHasBeenRefreshed: false,
      schemaRefreshing: false,
    });

    const { getByTestId } = renderComponent();

    expect(getByTestId("schemaChangesBackdrop")).toMatchSnapshot();
  });
  it("renders if there are non-breaking changes", () => {
    mockUseConnectionEditService.mockReturnValue({
      connection: { mockConnection, schemaChange: SchemaChange.non_breaking },
      schemaHasBeenRefreshed: false,
      schemaRefreshing: false,
    });

    const { getByTestId } = renderComponent();

    expect(getByTestId("schemaChangesBackdrop")).toMatchSnapshot();
  });
  it("does not render if there are no changes", () => {
    mockUseConnectionEditService.mockReturnValue({
      connection: { mockConnection, schemaChange: SchemaChange.no_change },
      schemaHasBeenRefreshed: false,
      schemaRefreshing: false,
    });

    const { queryByTestId } = renderComponent();

    expect(queryByTestId("schemaChangesBackdrop")).toBeFalsy();
  });
  it("does not render if schema has been refreshed", () => {
    mockUseConnectionEditService.mockReturnValue({
      connection: mockConnection,
      schemaHasBeenRefreshed: true,
      schemaRefreshing: false,
    });

    const { queryByTestId } = renderComponent();
    expect(queryByTestId("schemaChangesBackdrop")).toBeFalsy();
  });
});
