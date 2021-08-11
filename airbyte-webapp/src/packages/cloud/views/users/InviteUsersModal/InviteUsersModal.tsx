import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray, FieldProps, Form, Formik } from "formik";

import { Button, DropDown, H5, Input, LoadingButton, Modal } from "components";
import { Cell, Header, Row } from "components/SimpleTableComponents";
import { useGetUserService } from "packages/cloud/services/users/UserService";
import { useCurrentWorkspace } from "components/hooks/services/useWorkspace";

const Content = styled.div`
  width: 614px;
  padding: 20px 18px 75px 22px;
`;

const Controls = styled.div`
  display: flex;
  justify-content: center;
`;

const SendInvitationButton = styled(LoadingButton)`
  margin-left: 10px;
`;

export const InviteUsersModal: React.FC<{ onClose: () => void }> = (props) => {
  const formatMessage = useIntl().formatMessage;
  const userService = useGetUserService();
  const { workspaceId } = useCurrentWorkspace();
  const roleOptions = [
    {
      value: "admin",
      label: "admin",
    },
  ];
  return (
    <Modal
      title={<FormattedMessage id="modals.addUser.title" />}
      onClose={props.onClose}
    >
      <Formik
        initialValues={{
          users: [
            {
              email: "",
              role: undefined,
            },
          ],
        }}
        onSubmit={async (values) => {
          await userService.invite(values.users, workspaceId);
          props.onClose();
        }}
      >
        {({ values, isValid, isSubmitting, dirty }) => (
          <Form>
            <Content>
              <Header>
                <Cell>
                  <H5>
                    <FormattedMessage id="modals.addUser.email.label" />
                  </H5>
                </Cell>
                <Cell>
                  <H5>
                    <FormattedMessage id="modals.addUser.role.label" />
                  </H5>
                </Cell>
              </Header>
              <FieldArray
                name="users"
                render={(arrayHelpers) => (
                  <>
                    {values.users?.map((_, index) => (
                      <Row>
                        <Cell>
                          <Field name={`users[${index}].email`}>
                            {({ field }: FieldProps<string>) => (
                              <Input
                                {...field}
                                placeholder="email@company.com"
                              />
                            )}
                          </Field>
                        </Cell>
                        <Cell>
                          <Field
                            name={`users.${index}.role`}
                            placeholder={formatMessage({
                              id: "modals.addUser.role.placeholder",
                            })}
                            options={roleOptions}
                            component={DropDown}
                          />
                        </Cell>
                      </Row>
                    ))}
                    <Button type="button" onClick={() => arrayHelpers.push({})}>
                      <FormattedMessage id="modals.addUser.button.addUser" />
                    </Button>
                  </>
                )}
              />

              <Controls>
                <Button secondary onClick={props.onClose}>
                  <FormattedMessage id="modals.addUser.button.cancel" />
                </Button>
                <SendInvitationButton
                  type="submit"
                  disabled={!isValid || !dirty}
                  isLoading={isSubmitting}
                >
                  <FormattedMessage id="modals.addUser.button.submit" />
                </SendInvitationButton>
              </Controls>
            </Content>
          </Form>
        )}
      </Formik>
    </Modal>
  );
};
