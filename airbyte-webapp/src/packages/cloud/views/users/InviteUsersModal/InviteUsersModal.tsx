import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Field, FieldArray, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { H5 } from "components/base/Titles";
import { Cell, Header, Row } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";
import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { Modal } from "components/ui/Modal";
import { ToastType } from "components/ui/Toast";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useNotificationService } from "hooks/services/Notification";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useUserHook } from "packages/cloud/services/users/UseUserHook";

import styles from "./InviteUsersModal.module.scss";

const requestConnectorValidationSchema = yup.object({
  users: yup.array().of(
    yup.object().shape({
      role: yup.string().required("form.empty.error"),
      email: yup.string().required("form.empty.error").email("form.email.error"),
    })
  ),
});

const Content = styled.div`
  width: 614px;
  padding: 20px 18px 37px 22px;
`;

const Controls = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-top: 26px;
`;

const FormHeader = styled(Header)`
  margin-bottom: 14px;
`;

const FormRow = styled(Row)`
  margin-bottom: 8px;
`;

const ROLE_OPTIONS = [
  {
    value: "admin",
    label: "admin",
  },
];

export const InviteUsersModal: React.FC<{
  onClose: () => void;
  invitedFrom: "source" | "destination" | "user.settings";
}> = (props) => {
  const { formatMessage } = useIntl();
  const { workspaceId } = useCurrentWorkspace();
  const { inviteUserLogic } = useUserHook();
  const { registerNotification } = useNotificationService();
  const { mutateAsync: invite } = inviteUserLogic;

  const isRoleVisible = false; // Temporarily hiding roles because there's only 'Admin' in cloud.
  const analyticsService = useAnalyticsService();
  return (
    <Modal title={<FormattedMessage id="modals.addUser.title" />} onClose={props.onClose}>
      <Formik
        validateOnBlur
        validateOnChange
        validationSchema={requestConnectorValidationSchema}
        initialValues={{
          users: [
            {
              email: "",
              role: ROLE_OPTIONS[0].value,
            },
          ],
        }}
        onSubmit={async (values) => {
          await invite(
            { users: values.users, workspaceId },
            {
              onSuccess: () => {
                registerNotification({
                  text: formatMessage({ id: "addUsers.success.title" }),
                  id: "invite-users-success",
                  type: ToastType.SUCCESS,
                });
                props.onClose();
              },
            }
          );
          analyticsService.track(Namespace.USER, Action.INVITE, {
            invited_from: props.invitedFrom,
          });
        }}
      >
        {({ values, isValid, isSubmitting, dirty, setFieldValue }) => {
          return (
            <Form>
              <Content>
                <FormHeader>
                  <Cell flex={2}>
                    <H5>
                      <FormattedMessage id="modals.addUser.email.label" />
                    </H5>
                  </Cell>
                  {isRoleVisible && (
                    <Cell>
                      <H5>
                        <FormattedMessage id="modals.addUser.role.label" />
                      </H5>
                    </Cell>
                  )}
                </FormHeader>
                <FieldArray
                  name="users"
                  render={(arrayHelpers) => (
                    <>
                      {values.users?.map((_, index) => (
                        <FormRow>
                          <Cell flex={2}>
                            <Field name={`users[${index}].email`}>
                              {({ field }: FieldProps<string>) => <Input {...field} placeholder="email@company.com" />}
                            </Field>
                          </Cell>
                          {isRoleVisible && (
                            <Cell>
                              <Field name={`users[${index}].role`}>
                                {({ field }: FieldProps) => {
                                  return (
                                    <DropDown
                                      isDisabled
                                      value={field.value}
                                      placeholder={formatMessage({
                                        id: "modals.addUser.role.placeholder",
                                      })}
                                      options={ROLE_OPTIONS}
                                    />
                                  );
                                }}
                              </Field>
                            </Cell>
                          )}
                          <Button
                            className={styles.deleteButton}
                            type="button"
                            disabled={values.users.length < 2}
                            onClick={() => {
                              setFieldValue("users", [
                                ...values.users.slice(0, index),
                                ...values.users.slice(index + 1),
                              ]);
                            }}
                            variant="secondary"
                            icon={<FontAwesomeIcon icon={faTimes} />}
                          />
                        </FormRow>
                      ))}
                      <Button
                        type="button"
                        disabled={!isValid || !dirty}
                        onClick={() =>
                          arrayHelpers.push({
                            email: "",
                            role: ROLE_OPTIONS[0].value,
                          })
                        }
                        variant="secondary"
                      >
                        <FormattedMessage id="modals.addUser.button.addUser" />
                      </Button>
                    </>
                  )}
                />

                <Controls>
                  <Button type="button" variant="secondary" onClick={props.onClose}>
                    <FormattedMessage id="modals.addUser.button.cancel" />
                  </Button>
                  <Button
                    className={styles.sendInvitationButton}
                    data-testid="modals.addUser.button.submit"
                    type="submit"
                    disabled={!isValid || !dirty}
                    isLoading={isSubmitting}
                  >
                    <FormattedMessage id="modals.addUser.button.submit" />
                  </Button>
                </Controls>
              </Content>
            </Form>
          );
        }}
      </Formik>
    </Modal>
  );
};
