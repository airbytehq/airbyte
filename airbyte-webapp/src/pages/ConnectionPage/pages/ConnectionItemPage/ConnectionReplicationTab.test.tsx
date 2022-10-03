import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { mockConnection, TestWrapper } from "test-utils/testutils";

import { ModalServiceProvider } from "hooks/services/Modal";
import { ConfigProvider } from "packages/cloud/services/ConfigProvider";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";

import { ConnectionReplicationTab } from "./ConnectionReplicationTab";

jest.mock("hooks/services/ConnectionEdit/ConnectionEditService", () => {
  let schemaHasBeenRefreshed = false;
  return {
    useConnectionEditService: () => ({
      connection: mockConnection,
      schemaRefreshing: false,
      schemaHasBeenRefreshed,
      updateConnection: jest.fn(),
      setSchemaHasBeenRefreshed: (s: boolean) => (schemaHasBeenRefreshed = s),
    }),
  };
});

//   const { connection, schemaRefreshing, schemaHasBeenRefreshed, updateConnection, setSchemaHasBeenRefreshed } =
// useConnectionEditService();

describe("ConnectionReplicationTab", () => {
  const Wrapper: React.FC<Parameters<typeof ConnectionReplicationTab>[0]> = ({ children }) => (
    <TestWrapper>
      <MemoryRouter>
        <ModalServiceProvider>
          <ConfigProvider>
            <AnalyticsProvider>{children}</AnalyticsProvider>
          </ConfigProvider>
        </ModalServiceProvider>
      </MemoryRouter>
    </TestWrapper>
  );
  it("should render", () => {
    expect(
      render(
        <Wrapper>
          <ConnectionReplicationTab />
        </Wrapper>
      )
    ).toMatchSnapshot();
  });
});
