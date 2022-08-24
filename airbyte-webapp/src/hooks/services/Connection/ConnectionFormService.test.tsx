import { ReactNode } from "react";

import { render as tlr } from "utils/testutils";

import {
  ConnectionFormServiceProvider,
  ConnectionServiceProps,
  useConnectionFormService,
} from "./ConnectionFormService";

const mockWorkspace = {
  workspaceId: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  customerId: "55dd55e2-33ac-44dc-8d65-5aa7c8624f72",
  email: "krishna@airbyte.com",
  name: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  slug: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
  initialSetupComplete: true,
  displaySetupWizard: false,
  anonymousDataCollection: false,
  news: false,
  securityUpdates: false,
  notifications: [],
};

// ["services/workspaces/WorkspacesService", "../../../services/workspaces/WorkspacesService"].forEach((s) =>
// );
jest.mock("../../../services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspaceId: () => mockWorkspace.workspaceId,
  useCurrentWorkspace: () => mockWorkspace,
}));
jest.mock("../FormChangeTracker", () => ({
  useFormChangeTrackerService: () => ({ clearFormChange: () => null }),
  useUniqueFormId: () => "blah",
}));
jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({}));

describe("ConnectionFormService", () => {
  const render = (blah: ReactNode, props: ConnectionServiceProps) =>
    tlr(<ConnectionFormServiceProvider {...props}>{blah}</ConnectionFormServiceProvider>);

  const baseConnection: any = {
    destination: {
      destinationDefinitionId: "asdf",
    },
  };

  it("should render", () => {
    const onSubmit = jest.fn();
    const onAfterSubmit = jest.fn();
    const onFrequencySelect = jest.fn();
    const onCancel = jest.fn();

    const HookTester = () => {
      const connectionService = useConnectionFormService();
      expect(connectionService).toMatchSnapshot();
      return null;
    };

    render(HookTester, {
      connection: baseConnection,
      mode: "create",
      onSubmit,
      onAfterSubmit,
      onFrequencySelect,
      onCancel,
    });
  });
});
