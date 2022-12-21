import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, DropDownRow } from "components";
import { Separator } from "components/Separator";

import { ROLES } from "core/Constants/roles";

import AddUserModal from "./components/AddUserModal";
import ChangeRoleModal from "./components/ChangeRoleModal";
import DeleteUserModal from "./components/DeleteUserModal";
import UserTable from "./components/UserTable";
import { User } from "./components/UserTableBody";

const HeaderContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
`;

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 25px;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;

const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  color: #ffffff;
`;

const UserManagementPage: React.FC = () => {
  const [deleteModal, setDeleteModal] = useState<boolean>(false);
  const toggleDeleteModal = () => {
    setDeleteModal(!deleteModal);
  };
  const onDelete = () => {
    toggleDeleteModal();
  };

  const [changeRoleModal, setChangeRoleModal] = useState<boolean>(false);
  const toggleChangeRoleModal = () => {
    setChangeRoleModal(!changeRoleModal);
  };
  const onChangeRole = (option: DropDownRow.IDataItem) => {
    toggleChangeRoleModal();
    console.log(option);
  };

  const [addUserModal, setAddUserModal] = useState<boolean>(false);
  const toggleAddUserModal = () => {
    setAddUserModal(!addUserModal);
  };

  const users: User[] = [
    { _id: "1", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.Administrator_Owner, status: "Active" },
    { _id: "2", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.User, status: "Active" },
    { _id: "3", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.User, status: "Active" },
    { _id: "4", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.User, status: "Active" },
    { _id: "5", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.User, status: "Active" },
    { _id: "6", name: "Joe Doe", email: "janedoe@example.com", role: ROLES.User, status: "Pending" },
  ];

  const roles: DropDownRow.IDataItem[] = [
    { label: ROLES.Administrator, value: ROLES.Administrator },
    { label: ROLES.User, value: ROLES.User },
  ];

  return (
    <>
      <HeaderContainer>
        <Button onClick={toggleAddUserModal}>
          <BtnInnerContainer>
            <BtnIcon icon={faPlus} />
            <BtnText>
              <FormattedMessage id="user.newUser" />
            </BtnText>
          </BtnInnerContainer>
        </Button>
      </HeaderContainer>
      <Separator />
      <UserTable users={users} roles={roles} onDelete={onDelete} onChangeRole={onChangeRole} />
      {addUserModal && <AddUserModal roles={roles} onClose={toggleAddUserModal} />}
      {changeRoleModal && <ChangeRoleModal onClose={toggleChangeRoleModal} />}
      {deleteModal && <DeleteUserModal onClose={toggleDeleteModal} />}
    </>
  );
};

export default UserManagementPage;
