import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Input, Button, DropDownRow, LoadingButton, Modal, ModalBody } from "components";
import { DashIcon } from "components/icons/DashIcon";
import { Separator } from "components/Separator";

import { ROLES } from "core/Constants/roles";

import UserRoleDropDown from "./UserRoleDropdown";

interface NewUser {
  id: string;
  email: string;
  role: string;
}

interface IProps {
  roles: DropDownRow.IDataItem[];
  onClose?: () => void;
}

const ModalBodyContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 0;
`;

const ModalHeading = styled.div`
  font-weight: 700;
  font-size: 18px;
  line-height: 22px;
  color: ${({ theme }) => theme.black300};
`;

const FieldsContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const InputFieldContainer = styled.div`
  width: 45%;
`;

const InputFieldLabel = styled.div`
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: ${({ theme }) => theme.black300};
`;

const InputField = styled(Input)`
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 6px;
`;

const RemoveUserBtn = styled.button`
  width: 26px;
  height: 26px;
  border-radius: 30px;
  border: 2px solid #6b6b6f;
  background-color: transparent;
  cursor: pointer;
  margin-left: auto;
  padding: 0px 0px 6px 0px;
`;

const AddMoreBtn = styled.button`
  font-weight: 400;
  font-size: 14px;
  line-height: 16px;
  color: ${({ theme }) => theme.primaryColor};
  cursor: pointer;
  border: none;
  background-color: transparent;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;

const ButtonsContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
`;

const ChangeBtn = styled(LoadingButton)`
  margin-right: 48px;
`;

const AddUserModal: React.FC<IProps> = ({ roles, onClose }) => {
  const newUser: NewUser = { id: `${Math.random() * 1000 * Math.random()}`, email: "", role: ROLES.User };
  const [newUsers, setNewUsers] = useState<NewUser[]>([newUser]);

  const addUser = () => {
    setNewUsers((prevState) => {
      const users = [...prevState, newUser];
      return users;
    });
  };
  const removeUser = (userId: string) => {
    setNewUsers((prevState) => {
      const users = prevState.filter((user) => user.id !== userId);
      return users;
    });
  };
  return (
    <Modal size="lg" onClose={onClose}>
      <ModalBody>
        <ModalBodyContainer>
          <ModalHeading>
            <FormattedMessage id="user.addUserModal.heading" />
          </ModalHeading>
          <Separator height="30px" />
          <FieldsContainer>
            <InputFieldContainer style={{ marginRight: "30px" }}>
              <InputFieldLabel>Email</InputFieldLabel>
            </InputFieldContainer>
            <InputFieldContainer>
              <InputFieldLabel>Role</InputFieldLabel>
            </InputFieldContainer>
          </FieldsContainer>
          <Separator height="4px" />
          {newUsers.map((user, index) => (
            <>
              <FieldsContainer>
                <InputFieldContainer style={{ marginRight: "30px" }}>
                  <InputField value={user.email} />
                </InputFieldContainer>
                <InputFieldContainer>
                  <UserRoleDropDown value={user.role} options={roles} />
                </InputFieldContainer>
                {index !== 0 && (
                  <RemoveUserBtn onClick={() => removeUser(user.id)}>
                    <DashIcon color="#6B6B6F" width={13} />
                  </RemoveUserBtn>
                )}
              </FieldsContainer>
              <Separator height="20px" />
            </>
          ))}
          {newUsers.length >= 5 ? null : (
            <>
              <Separator height="10px" />
              <AddMoreBtn onClick={addUser}>
                <BtnIcon icon={faPlus} />
                <FormattedMessage id="user.addUserModal.addMoreBtn" />
              </AddMoreBtn>
            </>
          )}
          <Separator height="60px" />
          <ButtonsContainer>
            <ChangeBtn size="lg" secondary onClick={onClose}>
              <FormattedMessage id="user.addUserModal.cancelBtn" />
            </ChangeBtn>
            <Button size="lg" onClick={onClose} disabled>
              <FormattedMessage id="user.addUserModal.sendInviteBtn" />
            </Button>
          </ButtonsContainer>
        </ModalBodyContainer>
      </ModalBody>
    </Modal>
  );
};

export default AddUserModal;
