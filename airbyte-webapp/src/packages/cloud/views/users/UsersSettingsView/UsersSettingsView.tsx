import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ColumnDef } from "@tanstack/react-table";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { NextTable } from "components/ui/NextTable";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { User } from "packages/cloud/lib/domain/users";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import {
  InviteUsersModalServiceProvider,
  useInviteUsersModalService,
} from "packages/cloud/services/users/InviteUsersModalService";
import { useListUsers, useUserHook } from "packages/cloud/services/users/UseUserHook";

import styles from "./UsersSettingsView.module.scss";

const RemoveUserSection: React.VFC<{ workspaceId: string; email: string }> = ({ workspaceId, email }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { removeUserLogic } = useUserHook();
  const { isLoading, mutate: removeUser } = removeUserLogic;

  const onRemoveUserButtonClick = () => {
    openConfirmationModal({
      text: `modals.removeUser.text`,
      title: `modals.removeUser.title`,
      submitButtonText: "modals.removeUser.button.submit",
      onSubmit: async () => {
        removeUser({ email, workspaceId });
        closeConfirmationModal();
      },
      submitButtonDataId: "remove",
    });
  };

  return (
    <Button variant="secondary" onClick={onRemoveUserButtonClick} isLoading={isLoading}>
      <FormattedMessage id="userSettings.user.remove" />
    </Button>
  );
};

const Header: React.VFC = () => {
  const { toggleInviteUsersModalOpen } = useInviteUsersModalService();
  return (
    <div className={styles.header}>
      <Heading as="h1" size="sm">
        <FormattedMessage id="userSettings.table.title" />
      </Heading>
      <Button
        onClick={() => {
          toggleInviteUsersModalOpen();
        }}
        icon={<FontAwesomeIcon icon={faPlus} />}
        data-testid="userSettings.button.addNewUser"
      >
        <FormattedMessage id="userSettings.button.addNewUser" />
      </Button>
    </div>
  );
};

type ColumnDefs = [ColumnDef<User, string>, ColumnDef<User, string>, ColumnDef<User>];

export const UsersTable: React.FC = () => {
  const { workspaceId } = useCurrentWorkspace();
  const users = useListUsers();
  const { user } = useAuthService();

  const columns = useMemo<ColumnDefs>(
    () => [
      {
        header: () => <FormattedMessage id="userSettings.table.column.fullname" />,
        meta: {
          headerHighlighted: true,
        },
        accessorKey: "name",
        cell: (props) => props.cell.getValue(),
      },
      {
        header: () => <FormattedMessage id="userSettings.table.column.email" />,
        meta: {
          headerHighlighted: true,
        },
        accessorKey: "email",
        cell: (props) => props.cell.getValue(),
      },
      // TEMP: Currently all cloud users are admins.
      // Remove when there is more than role
      // {
      //   Header: (
      //     <>
      //       <FormattedMessage id="userSettings.table.column.role" />
      //       <RoleToolTip />
      //     </>
      //   ),
      //   headerHighlighted: true,
      //   accessor: "userId",
      //   Cell: (_: CellProps<User>) => "Admin",
      // },
      {
        header: () => <FormattedMessage id="userSettings.table.column.action" />,
        meta: {
          headerHighlighted: true,
        },
        accessorKey: "status",
        cell: (props) =>
          [
            user?.userId !== props.row.original.userId ? (
              <RemoveUserSection workspaceId={workspaceId} email={props.row.original.email} />
            ) : null,
          ].filter(Boolean),
      },
    ],
    [workspaceId, user]
  );

  return <NextTable data={users ?? []} columns={columns} />;
};

export const UsersSettingsView: React.VFC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_ACCESS_MANAGEMENT);

  return (
    <InviteUsersModalServiceProvider invitedFrom="user.settings">
      <Header />
      <UsersTable />
    </InviteUsersModalServiceProvider>
  );
};
