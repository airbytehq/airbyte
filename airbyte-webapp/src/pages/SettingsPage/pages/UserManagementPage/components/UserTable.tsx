import { Box, Typography } from "@mui/material";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDownRow, Tooltip } from "components";
import { QuestionIcon } from "components/icons/QuestionIcon";
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

const UserTable: React.FC<IProps> = React.memo(({ users, roles, onDelete, onChangeRole, onResendInvite }) => {
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
          <Tooltip
            control={
              <Box sx={{ display: "flex" }} pt={1}>
                <FormattedMessage id="user.heading.role" />
                <Box>
                  <QuestionIcon />
                </Box>
              </Box>
            }
            placement="top"
          >
            <Box>
              <Typography>
                <FormattedMessage id="permission.owner" />
              </Typography>
              .<FormattedMessage id="permission.owner.roleone" />
              <br />
              .<FormattedMessage id="permission.owner.roletwo" />
              <br />
              .<FormattedMessage id="permission.owner.rolethree" />
              <Typography>
                <FormattedMessage id="permission.admin" />
              </Typography>
              .<FormattedMessage id="permission.admin.role" />
              <Typography>
                <FormattedMessage id="permission.user" />
              </Typography>
              .<FormattedMessage id="permission.user.role" />
            </Box>
          </Tooltip>
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
});

export default UserTable;
