import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Field, FieldArray, FieldProps, Formik, Form as FormikForm } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as Yup from "yup";

import {
  // Input,
  Button,
  DropDownRow,
  LabeledInput,
  LoadingButton,
  Modal,
  ModalBody,
} from "components";
import { DashIcon } from "components/icons/DashIcon";
import { Separator } from "components/Separator";

import UserRoleDropDown from "./UserRoleDropdown";

interface NewUser {
  email: string;
  role: number;
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
  align-items: flex-end;
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

// const InputField = styled(Input)`
//   border: 1px solid #d1d5db;
//   background-color: white;
//   border-radius: 6px;
// `;

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
  const newUser: NewUser = { email: "", role: 3 };
  const { formatMessage } = useIntl();

  const addUserSchema = Yup.object({
    users: Yup.array().of(
      Yup.object().shape({
        email: Yup.string().required("email required").email("Enter valid email"),
        role: Yup.number(),
      })
    ),
  });
  return (
    <Modal size="lg" onClose={onClose}>
      <ModalBody>
        <Formik
          initialValues={{ users: [newUser] }}
          validationSchema={addUserSchema}
          onSubmit={(values) => {
            console.log(values);
          }}
          validateOnBlur
          validateOnChange
        >
          {({ values, isSubmitting, handleChange }) => {
            console.log(values);
            return (
              <ModalBodyContainer>
                <ModalHeading>
                  <FormattedMessage id="user.addUserModal.heading" />
                </ModalHeading>
                <Separator height="30px" />
                <FormikForm style={{ width: "100%" }}>
                  <FieldArray
                    name="users"
                    render={(arrayHandler) => {
                      return (
                        <>
                          {values.users.map((user, index) => {
                            return (
                              <>
                                <FieldsContainer>
                                  <InputFieldContainer style={{ marginRight: "30px" }}>
                                    <Field name={`users.${index}.email`}>
                                      {({ field, meta }: FieldProps<string>) => (
                                        <LabeledInput
                                          {...field}
                                          label={index === 0 && <FormattedMessage id="login.yourEmail" />}
                                          type="text"
                                          error={!!meta.error && meta.touched}
                                          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                                          style={{ width: "100%" }}
                                        />
                                      )}
                                    </Field>
                                  </InputFieldContainer>
                                  <InputFieldContainer>
                                    {index === 0 && (
                                      <>
                                        <InputFieldLabel>Role</InputFieldLabel>
                                        <Separator height="4px" />
                                      </>
                                    )}
                                    <UserRoleDropDown
                                      value={user.role}
                                      options={roles}
                                      onChange={(option) => handleChange(`users.${index}.role`)(option.value)}
                                      name={`users.${index}.role`}
                                    />
                                  </InputFieldContainer>
                                  {index !== 0 && (
                                    <RemoveUserBtn onClick={() => arrayHandler.remove(index)}>
                                      <DashIcon color="#6B6B6F" width={13} />
                                    </RemoveUserBtn>
                                  )}
                                </FieldsContainer>
                                <Separator />
                              </>
                            );
                          })}
                          {values.users.length >= 5 ? null : (
                            <>
                              <Separator height="10px" />
                              <AddMoreBtn onClick={() => arrayHandler.push(newUser)}>
                                <BtnIcon icon={faPlus} />
                                <FormattedMessage id="user.addUserModal.addMoreBtn" />
                              </AddMoreBtn>
                            </>
                          )}
                        </>
                      );
                    }}
                  />
                  <Separator height="60px" />
                  <ButtonsContainer>
                    <ChangeBtn size="lg" secondary onClick={onClose}>
                      <FormattedMessage id="user.addUserModal.cancelBtn" />
                    </ChangeBtn>
                    <Button
                      size="lg"
                      type="submit"
                      white
                      // disabled={!(isValid && dirty)}
                      isLoading={isSubmitting}
                    >
                      <FormattedMessage id="user.addUserModal.sendInviteBtn" />
                    </Button>
                  </ButtonsContainer>
                </FormikForm>
              </ModalBodyContainer>
            );
          }}
        </Formik>
      </ModalBody>
    </Modal>
  );
};

export default AddUserModal;
