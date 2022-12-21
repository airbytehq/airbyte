import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDownRow } from "components";
import { Tooltip } from "components/base/Tooltip";
import { DeleteIcon } from "components/icons/DeleteIcon";
import { RefreshIcon } from "components/icons/RefreshIcon";
import { Row, Cell } from "components/SimpleTableComponents";

import { ROLES } from "core/Constants/roles";

import UserRoleDropdown from "./UserRoleDropdown";

export interface User {
  _id: string;
  name: string;
  email: string;
  role: string;
  status: string;
}

interface IProps {
  users: User[];
  roles: DropDownRow.IDataItem[];
  onDelete: () => void;
  onChangeRole: (option: DropDownRow.IDataItem) => void;
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

const UserTableBody: React.FC<IProps> = ({ users, roles, onDelete, onChangeRole }) => {
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
            <UserRoleDropdown value={user.role} options={roles} onChange={onChangeRole} />
          </BodyCell>
          <BodyCell>{user.status}</BodyCell>
          <BodyCell>
            <ActionCell>
              {user.role !== ROLES.Administrator_Owner && (
                <Tooltip
                  control={
                    <ActionBtn onClick={onDelete}>
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
                    <ActionBtn>
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
