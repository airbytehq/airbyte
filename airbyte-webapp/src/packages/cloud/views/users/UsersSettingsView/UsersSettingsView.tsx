import React from "react";
import styled from "styled-components";
import { CellProps } from "react-table";
import { FormattedMessage } from "react-intl";
import { useQuery } from "react-query";
import { useToggle } from "react-use";

import { Button, H5 } from "components";
import Table from "components/Table";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetUserService } from "packages/cloud/services/users/UserService";
import { InviteUsersModal } from "packages/cloud/views/users/InviteUsersModal";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useUserHook } from "packages/cloud/services/users/UseUserHook";
import { User } from "packages/cloud/lib/domain/users";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
`;

export const UsersSettingsView: React.FC = () => {
  const [modalIsOpen, toggleModal] = useToggle(false);
  const userService = useGetUserService();
  const { workspaceId } = useCurrentWorkspace();

  const { data, refetch } = useQuery(
    ["users", workspaceId],
    () => userService.listByWorkspaceId(workspaceId),
    { suspense: true }
  );

  // TODO: show error with request fails
  const { isLoading, mutate } = useUserHook(console.log, console.log);

  const { user } = useAuthService();

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="userSettings.table.column.fullname" />,
        headerHighlighted: true,
        accessor: "name",
        Cell: ({ cell }: CellProps<any>) => cell.value,
      },
      {
        Header: <FormattedMessage id="userSettings.table.column.email" />,
        headerHighlighted: true,
        accessor: "email",
        Cell: ({ cell }: CellProps<any>) => cell.value,
      },
      {
        Header: <FormattedMessage id="userSettings.table.column.role" />,
        headerHighlighted: true,
        accessor: "userId",
        Cell: (_: CellProps<any>) => "admin",
      },
      {
        Header: <FormattedMessage id="userSettings.table.column.action" />,
        headerHighlighted: true,
        accessor: "status",
        Cell: ({ row }: CellProps<User>) =>
          [
            <Button
              disabled={user?.userId === row.original.userId}
              secondary
              onClick={() => mutate(row.original.userId)}
              isLoading={isLoading}
            >
              <FormattedMessage id="userSettings.user.remove" />
            </Button>,
            // cell.value === "invited" && <Button secondary>send again</Button>,
          ].filter(Boolean),
      },
    ],
    [isLoading, mutate]
  );

  return (
    <>
      <Header>
        <H5>
          <FormattedMessage id="userSettings.table.title" />
        </H5>
        <Button onClick={toggleModal}>
          + <FormattedMessage id="userSettings.button.addNewUser" />
        </Button>
      </Header>
      <Table data={data ?? []} columns={columns} />
      {modalIsOpen && (
        <InviteUsersModal onClose={toggleModal} onSubmit={() => refetch()} />
      )}
    </>
  );
};
