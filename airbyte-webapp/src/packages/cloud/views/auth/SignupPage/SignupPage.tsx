import React from "react";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Formik } from "formik";
import styled from "styled-components";

import {
  BottomBlock,
  FieldItem,
  Form,
  RowFieldItem,
} from "../components/FormComponents";
import { Button, H4, LabeledInput, LabeledToggle } from "components";
import { FormTitle } from "../components/FormTitle";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FieldError } from "packages/cloud/lib/errors/FieldError";

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  company: yup.string().required("form.empty.error"),
  security: yup.boolean().required("form.empty.error"),
});

const SignupPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const { signUp } = useAuthService();

  return (
    <div>
      <FormTitle bold>Activate your free beta access</FormTitle>
      <H4>No credit card required. Free until official launch.</H4>

      <Formik
        initialValues={{
          name: "",
          company: "",
          email: "",
          password: "",
          subscribe: true,
          security: false,
        }}
        validationSchema={SignupPageValidationSchema}
        onSubmit={async (values, { setFieldError, setStatus }) =>
          signUp(values).catch((err) => {
            if (err instanceof FieldError) {
              setFieldError(err.field, err.message);
            } else {
              setStatus(err.message);
            }
          })
        }
        validateOnBlur={true}
        validateOnChange={false}
      >
        {() => (
          <Form>
            <RowFieldItem>
              <Field name="name">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label="name"
                    placeholder="name"
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
              <Field name="company">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label="company"
                    placeholder="company"
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </RowFieldItem>
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="form.yourEmail" />}
                    placeholder={formatMessage({
                      id: "form.email.placeholder",
                    })}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem>
              <Field name="password">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label="Password"
                    placeholder="ss"
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem>
              <Field name="subscribe">
                {({ field, meta }: FieldProps<string>) => (
                  <MarginBlock>
                    <LabeledToggle
                      {...field}
                      checked={!!field.value}
                      checkbox
                      label={"subscribe"}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
                    />
                  </MarginBlock>
                )}
              </Field>
              <Field name="security">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledToggle
                    {...field}
                    checked={!!field.value}
                    checkbox
                    label={"security"}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <BottomBlock>
              <>
                <div />
                <Button type="submit">Sign Up</Button>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default SignupPage;
