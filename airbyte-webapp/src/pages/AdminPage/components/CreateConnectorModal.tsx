import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import Modal from "../../../components/Modal";
import Button from "../../../components/Button";
import Link from "../../../components/Link";
import { Field, FieldProps, Form, Formik } from "formik";
import LabeledInput from "../../../components/LabeledInput";
import config from "../../../config";

export type IProps = {
  onClose: () => void;
  onSubmit: (source: { name: string; dockerRepository: string }) => void;
};

const Content = styled.div`
  width: 585px;
  padding: 19px 41px 36px 36px;
`;

const ButtonContent = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 12px;
`;

const Label = styled.div`
  font-weight: bold;
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 8px;
`;

const FieldContainer = styled.div`
  margin-bottom: 21px;
`;

const DocLink = styled(Link).attrs({ as: "a" })`
  margin-bottom: 8px;
  text-decoration: none;
  display: block;
`;

const validationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
  dockerRepository: yup.string().required("form.empty.error")
});

const CreateConnectorModal: React.FC<IProps> = ({ onClose, onSubmit }) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <Modal
      onClose={onClose}
      title={<FormattedMessage id="admin.addNewConnector" />}
    >
      <Content>
        <Formik
          initialValues={{
            name: "",
            dockerRepository: ""
          }}
          validateOnBlur={true}
          validateOnChange={true}
          validationSchema={validationSchema}
          onSubmit={async (values, { setSubmitting }) => {
            await onSubmit(values);
            setSubmitting(false);
          }}
        >
          {({ isSubmitting, dirty, isValid }) => (
            <Form>
              <FieldContainer>
                <Field name="name">
                  {({ field }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      type="text"
                      placeholder={formatMessage({
                        id: "admin.connectorName.placeholder"
                      })}
                      label={
                        <Label>
                          <FormattedMessage id="admin.connectorName" />
                        </Label>
                      }
                    />
                  )}
                </Field>
              </FieldContainer>
              <FieldContainer>
                <Field name="dockerRepository">
                  {({ field }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      type="text"
                      autoComplete="off"
                      placeholder={formatMessage({
                        id: "admin.dockerRepository.placeholder"
                      })}
                      label={
                        <>
                          <Label>
                            <FormattedMessage id="admin.dockerRepository" />
                          </Label>
                          <FormattedMessage id="admin.locationOfDocker" />
                          <DocLink
                            as="a"
                            href={config.ui.docsLink}
                            target="_blank"
                          >
                            <FormattedMessage id="admin.learnMore" />
                          </DocLink>
                        </>
                      }
                    />
                  )}
                </Field>
              </FieldContainer>
              <ButtonContent>
                <ButtonWithMargin onClick={onClose} type="button" secondary>
                  <FormattedMessage id="form.cancel" />
                </ButtonWithMargin>
                <Button
                  type="submit"
                  disabled={isSubmitting || !dirty || !isValid}
                >
                  <FormattedMessage id="form.add" />
                </Button>
              </ButtonContent>
            </Form>
          )}
        </Formik>
      </Content>
    </Modal>
  );
};

export default CreateConnectorModal;
