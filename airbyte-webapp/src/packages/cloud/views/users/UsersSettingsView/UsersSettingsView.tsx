import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import { useToggle } from "react-use";

import { H5 } from "components/base/Titles";
import { Button } from "components/ui/Button";
import { Table } from "components/ui/Table";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { User } from "packages/cloud/lib/domain/users";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useListUsers, useUserHook } from "packages/cloud/services/users/UseUserHook";
import { InviteUsersModal } from "packages/cloud/views/users/InviteUsersModal";

import styles from "./UsersSettingsView.module.scss";

const RemoveUserSection: React.FC<{ workspaceId: string; email: string }> = ({ workspaceId, email }) => {
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

export const UsersSettingsView: React.FC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_ACCESS_MANAGEMENT);

  const [modalIsOpen, toggleModal] = useToggle(false);
  const { workspaceId } = useCurrentWorkspace();

  const users = useListUsers();

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
        Header: <FormattedMessage id="userSettings.table.column.action" />,
        headerHighlighted: true,
        accessor: "status",
        Cell: ({ row }: CellProps<User>) =>
          [
            user?.userId !== row.original.userId ? (
              <RemoveUserSection workspaceId={workspaceId} email={row.original.email} />
            ) : null,
          ].filter(Boolean),
      },
    ],
    [workspaceId, user]
  );

  return (
    <>
      <div className={styles.header}>
        <H5>
          <FormattedMessage id="userSettings.table.title" />
        </H5>
        <Button
          data-testid="userSettings.button.addNewUser"
          icon={<FontAwesomeIcon icon={faPlus} />}
          onClick={toggleModal}
        >
          <FormattedMessage id="userSettings.button.addNewUser" />
        </Button>
      </div>
      <Table data={users ?? []} columns={columns} />
      {modalIsOpen && <InviteUsersModal onClose={toggleModal} />}
    </>
  );
};
