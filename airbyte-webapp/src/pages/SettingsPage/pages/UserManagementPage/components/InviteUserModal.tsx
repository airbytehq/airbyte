import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Field, FieldArray, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { Button, DropDownRow, LabeledInput, LoadingButton, Modal, ModalBody } from "components";
import { DashIcon } from "components/icons/DashIcon";
import { Separator } from "components/Separator";

import { useUserAsyncAction } from "services/users/UsersService";

import UserRoleDropDown from "./UserRoleDropdown";

interface IProps {
  roles: DropDownRow.IDataItem[];
  onClose?: () => void;
  setMessageId: React.Dispatch<React.SetStateAction<string>>;
  setMessageType: React.Dispatch<React.SetStateAction<"info" | "error">>;
}

const ModalBodyContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 16px 10px 26px 10px;
`;

const ModalHeading = styled.div`
  font-weight: 700;
  font-size: 18px;
  line-height: 22px;
  color: ${({ theme }) => theme.black300};
`;

const Controls = styled.div`
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-top: 60px;
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

const SendInvitationButton = styled(LoadingButton)`
  margin-left: 10px;
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

const CancelBtn = styled(Button)`
  margin-right: 48px;
`;

const AddMoreBtn = styled(Button)`
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

const AddUserModal: React.FC<IProps> = ({ onClose, roles, setMessageId, setMessageType }) => {
  const [loading, setLoading] = useState(false);

  const inviteUsersSchema = yup.object({
    users: yup.array().of(
      yup.object().shape({
        email: yup
          .string()
          .required("user.addUserModal.email.empty.error")
          .email("user.addUserModal.email.valid.error"),
        role: yup.string().required("user.addUserModal.role.empty.error"),
      })
    ),
  });

  const { formatMessage } = useIntl();
  const { onAddUser } = useUserAsyncAction();
  return (
    <Modal size="lg" onClose={() => onClose?.()}>
      <ModalBody>
        <Formik
          validateOnBlur
          validateOnChange
          validationSchema={inviteUsersSchema}
          initialValues={{ users: [{ email: "", role: 3 }] }}
          onSubmit={(values) => {
            const { users } = values;
            setLoading(true);
            onAddUser(users)
              .then(() => {
                setLoading(false);
                onClose?.();
              })
              .catch((error: any) => {
                setLoading(false);
                setMessageId(error.message);
                setMessageType("error");
              });
          }}
        >
          {({ values, isValid, dirty, setFieldValue }) => {
            return (
              <Form>
                <ModalBodyContainer>
                  <ModalHeading>
                    <FormattedMessage id="user.addUserModal.heading" />
                  </ModalHeading>
                  <Separator height="30px" />
                  <FieldArray
                    name="users"
                    render={(arrayHelpers) => (
                      <>
                        {values.users?.map((_, index) => (
                          <>
                            <FieldsContainer>
                              <InputFieldContainer style={{ marginRight: "30px" }}>
                                <Field name={`users[${index}].email`}>
                                  {({ field, meta }: FieldProps<string>) => (
                                    <LabeledInput
                                      {...field}
                                      label={
                                        index === 0 && <FormattedMessage id="user.addUserModal.email.fieldLabel" />
                                      }
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
                                    <InputFieldLabel>
                                      <FormattedMessage id="user.addUserModal.role.fieldLabel" />
                                    </InputFieldLabel>
                                    <Separator height="4px" />
                                  </>
                                )}
                                <Field name={`users[${index}].role`}>
                                  {({ field }: FieldProps) => {
                                    return (
                                      <UserRoleDropDown
                                        value={field.value}
                                        options={roles}
                                        onChange={(option) => {
                                          setFieldValue(field.name, option.value);
                                        }}
                                      />
                                    );
                                  }}
                                </Field>
                              </InputFieldContainer>
                              {index !== 0 && (
                                <RemoveUserBtn
                                  onClick={() => {
                                    setFieldValue("users", [
                                      ...values.users.slice(0, index),
                                      ...values.users.slice(index + 1),
                                    ]);
                                  }}
                                >
                                  <DashIcon color="#6B6B6F" width={13} />
                                </RemoveUserBtn>
                              )}
                            </FieldsContainer>
                            <Separator />
                          </>
                        ))}
                        {values.users.length >= 5 ? null : (
                          <AddMoreBtn
                            type="button"
                            disabled={!isValid || !dirty}
                            onClick={() => arrayHelpers.push({ email: "", role: 3 })}
                            secondary
                          >
                            <BtnIcon icon={faPlus} />
                            <FormattedMessage id="user.addUserModal.addMoreBtn" />
                          </AddMoreBtn>
                        )}
                      </>
                    )}
                  />
                  <Controls>
                    <CancelBtn size="lg" type="button" secondary onClick={() => onClose?.()}>
                      <FormattedMessage id="user.addUserModal.cancelBtn" />
                    </CancelBtn>
                    <SendInvitationButton
                      data-testid="user.addUserModal.sendInviteBtn"
                      size="lg"
                      white
                      type="submit"
                      disabled={!isValid || !dirty}
                      isLoading={loading}
                    >
                      <FormattedMessage id="user.addUserModal.sendInviteBtn" />
                    </SendInvitationButton>
                  </Controls>
                </ModalBodyContainer>
              </Form>
            );
          }}
        </Formik>
      </ModalBody>
    </Modal>
  );
};

export default AddUserModal;
