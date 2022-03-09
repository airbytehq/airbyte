import React from "react";
import styled from "styled-components";
import { CellProps } from "react-table";
import { FormattedMessage } from "react-intl";
import { useToggle } from "react-use";

import { Button, H5, LoadingButton } from "components";
import Table from "components/Table";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { InviteUsersModal } from "packages/cloud/views/users/InviteUsersModal";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import {
  useListUsers,
  useUserHook,
} from "packages/cloud/services/users/UseUserHook";
import { User } from "packages/cloud/lib/domain/users";
import RoleToolTip from "./components/RoleToolTip";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
`;

const RemoveUserSection: React.FC<{ workspaceId: string; email: string }> = ({
  workspaceId,
  email,
}) => {
  const { removeUserLogic } = useUserHook();
  const { isLoading, mutate: removeUser } = removeUserLogic;

  return (
    <LoadingButton
      secondary
      onClick={() => removeUser({ email, workspaceId })}
      isLoading={isLoading}
    >
      <FormattedMessage id="userSettings.user.remove" />
    </LoadingButton>
  );
};

export const UsersSettingsView: React.FC = () => {
  const [modalIsOpen, toggleModal] = useToggle(false);
  const { workspaceId } = useCurrentWorkspace();

  const { data: users } = useListUsers();

  const { user } = useAuthService();

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="userSettings.table.column.fullname" />,
        headerHighlighted: true,
        accessor: "name",
        Cell: ({ cell }: CellProps<User>) => cell.value,
      },
      {
        Header: <FormattedMessage id="userSettings.table.column.email" />,
        headerHighlighted: true,
        accessor: "email",
        Cell: ({ cell }: CellProps<User>) => cell.value,
      },
      {
        Header: (
          <>
            <FormattedMessage id="userSettings.table.column.role" />
            <RoleToolTip />
          </>
        ),
        headerHighlighted: true,
        accessor: "userId",
        Cell: (_: CellProps<User>) => "admin",
      },
      {
        Header: <FormattedMessage id="userSettings.table.column.action" />,
        headerHighlighted: true,
        accessor: "status",
        Cell: ({ row }: CellProps<User>) =>
          [
            user?.userId !== row.original.userId ? (
              <RemoveUserSection
                workspaceId={workspaceId}
                email={row.original.email}
              />
            ) : null,
            // cell.value === "invited" && <Button secondary>send again</Button>,
          ].filter(Boolean),
      },
    ],
    [workspaceId, user]
  );

  return (
    <>
      <Header>
        <H5>
          <FormattedMessage id="userSettings.table.title" />
        </H5>
        <Button
          onClick={toggleModal}
          data-testid="userSettings.button.addNewUser"
        >
          + <FormattedMessage id="userSettings.button.addNewUser" />
        </Button>
      </Header>
      <Table data={users ?? []} columns={columns} />
      {modalIsOpen && <InviteUsersModal onClose={toggleModal} />}
    </>
  );
};
