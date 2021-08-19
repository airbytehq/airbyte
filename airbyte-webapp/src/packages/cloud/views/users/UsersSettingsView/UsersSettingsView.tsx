import React from "react";
import styled from "styled-components";
import { CellProps } from "react-table";
import { FormattedMessage } from "react-intl";
import { useQuery } from "react-query";
import { useToggle } from "react-use";

import { Button, H5 } from "components";
import Table from "components/Table";
import { useCurrentWorkspace } from "components/hooks/services/useWorkspace";
import { useGetUserService } from "packages/cloud/services/users/UserService";
import { InviteUsersModal } from "packages/cloud/views/users/InviteUsersModal";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
`;

export const UsersSettingsView: React.FC = () => {
  const userService = useGetUserService();
  const { workspaceId } = useCurrentWorkspace();
  const { data } = useQuery(
    ["users"],
    () => userService.listByWorkspaceId(workspaceId),
    { suspense: true }
  );

  const [modalIsOpen, toggleModal] = useToggle(false);

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
        Cell: (_: CellProps<any>) =>
          [
            <Button secondary>
              <FormattedMessage id="userSettings.user.remove" />
            </Button>,
            // cell.value === "invited" && <Button secondary>send again</Button>,
          ].filter(Boolean),
      },
    ],
    []
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
      {modalIsOpen && <InviteUsersModal onClose={toggleModal} />}
    </>
  );
};
