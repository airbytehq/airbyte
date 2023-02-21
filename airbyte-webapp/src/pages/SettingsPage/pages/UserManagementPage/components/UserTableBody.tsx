import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDownRow } from "components";
import { Tooltip } from "components/base/Tooltip";
import { DeleteIcon } from "components/icons/DeleteIcon";
import { RefreshIcon } from "components/icons/RefreshIcon";
import { Row, Cell } from "components/SimpleTableComponents";

import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";
import { User } from "core/domain/user";

import UserRoleDropdown from "./UserRoleDropdown";

interface IProps {
  users: User[];
  roles: DropDownRow.IDataItem[];
  onDelete: (userId: string) => void;
  onChangeRole: (userId: string, option: DropDownRow.IDataItem) => void;
  onResendInvite: (userId: string) => void;
}

const BodyRow = styled(Row)<{
  isBackgroundTransparent: boolean;
  isLastRow: boolean;
}>`
  padding: 30px 0;
  background-color: ${({ isBackgroundTransparent }) => (isBackgroundTransparent ? "transparent" : "#F8F8FE")};
  border-radius: ${({ isLastRow }) => (isLastRow ? "0 0 6px 6px" : 0)};
`;

const BodyCell = styled(Cell)`
  font-weight: 400;
  font-size: 13px;
  line-height: 13px;
  color: ${({ theme }) => theme.black300};
`;

const ActionCell = styled.div`
  width: 75px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
`;

const ActionBtn = styled.button`
  padding: 0px;
  cursor: pointer;
  border: none;
  background-color: transparent;
`;

const UserTableBody: React.FC<IProps> = ({ users, roles, onDelete, onChangeRole, onResendInvite }) => {
  return (
    <>
      {users.map((user, index) => (
        <BodyRow
          isBackgroundTransparent={index % 2 === 0 ? true : false}
          isLastRow={users.length === index + 1 ? true : false}
        >
          <BodyCell style={{ marginLeft: "40px" }}>{user.name}</BodyCell>
          <BodyCell>{user.email}</BodyCell>
          <BodyCell>
            <UserRoleDropdown
              value={user.roleIndex}
              roleDesc={user.roleDesc}
              options={roles}
              onChange={(option) => onChangeRole(user.id, option)}
            />
          </BodyCell>
          <BodyCell>{user.statusLang}</BodyCell>
          <BodyCell>
            <ActionCell>
              {getRoleAgainstRoleNumber(user.roleIndex) !== ROLES.Administrator_Owner && (
                <Tooltip
                  control={
                    <ActionBtn onClick={() => onDelete(user.id)}>
                      <DeleteIcon color="#6B6B6F" />
                    </ActionBtn>
                  }
                  placement="top"
                  theme="dark"
                >
                  <FormattedMessage id="user.actionBtn.delete" />
                </Tooltip>
              )}
              {user.status === "Pending" && (
                <Tooltip
                  control={
                    <ActionBtn onClick={() => onResendInvite(user.id)}>
                      <RefreshIcon color="#6B6B6F" />
                    </ActionBtn>
                  }
                  placement="top"
                  theme="dark"
                >
                  <FormattedMessage id="user.actionBtn.resendInvite" />
                </Tooltip>
              )}
            </ActionCell>
          </BodyCell>
        </BodyRow>
      ))}
    </>
  );
};

export default UserTableBody;
