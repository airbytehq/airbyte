import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDownRow } from "components";
import { Row, Cell } from "components/SimpleTableComponents";

import { User } from "core/domain/user";

import UserTableBody from "./UserTableBody";

interface IProps {
  users: User[];
  roles: DropDownRow.IDataItem[];
  onDelete: (userId: string) => void;
  onChangeRole: (userId: string, option: DropDownRow.IDataItem) => void;
  onResendInvite: (userId: string) => void;
}

const TableContainer = styled.div`
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
`;

const HeaderRow = styled(Row)`
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid #d1d5db;
`;

const HeaderCell = styled(Cell)`
  font-weight: 500;
  font-size: 13px;
  line-height: 13px;
  color: #6b6b6f;
`;

const UserTable: React.FC<IProps> = ({ users, roles, onDelete, onChangeRole, onResendInvite }) => {
  return (
    <TableContainer>
      <HeaderRow style={{ padding: "20px 0" }}>
        <HeaderCell style={{ marginLeft: "40px" }}>
          <FormattedMessage id="user.heading.name" />
        </HeaderCell>
        <HeaderCell>
          <FormattedMessage id="user.heading.email" />
        </HeaderCell>
        <HeaderCell>
          <FormattedMessage id="user.heading.role" />
        </HeaderCell>
        <HeaderCell>
          <FormattedMessage id="user.heading.status" />
        </HeaderCell>
        <HeaderCell>
          <FormattedMessage id="user.heading.action" />
        </HeaderCell>
      </HeaderRow>
      <UserTableBody
        users={users}
        roles={roles}
        onDelete={onDelete}
        onChangeRole={onChangeRole}
        onResendInvite={onResendInvite}
      />
    </TableContainer>
  );
};

export default UserTable;
