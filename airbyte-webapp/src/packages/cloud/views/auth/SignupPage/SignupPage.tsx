import React from "react";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Formik } from "formik";
import styled from "styled-components";

import { useConfig } from "config";

import {
  BottomBlock,
  FieldItem,
  Form,
  RowFieldItem,
} from "../components/FormComponents";
import { Button, H1, LabeledInput, Link } from "components";
import CheckBoxControl from "../components/CheckBoxControl";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FieldError } from "packages/cloud/lib/errors/FieldError";

type FormValues = {
  name: string;
  company: string;
  email: string;
  password: string;
  subscribe: boolean;
  security: boolean;
};

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

const HighlightBlock = styled.span<{ red?: boolean }>`
  color: ${({ theme, red }) => (red ? theme.redColor : "inhered")};
  font-family: ${({ theme }) => theme.italicFont};
`;

const SpecialOffer = styled.div`
  margin-top: 27px;
  background: ${({ theme }) => theme.redTransparentColor};
  border-radius: 12px;
  padding: 14px 8px 14px 19px;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
`;

const SumBlock = styled.span`
  display: inline-block;
  background: ${({ theme }) => theme.lightRedColor};
  border: 4px solid ${({ theme }) => theme.redColor};
  box-sizing: border-box;
  box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
  border-radius: 8px;
  font-family: ${({ theme }) => theme.italicFont};
  padding: 0 5px;
`;

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  company: yup.string().required("form.empty.error"),
  security: yup.boolean().oneOf([true], "form.empty.error"),
});

const SignupPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const config = useConfig();

  const { signUp } = useAuthService();

  const isSignUpDisabled = (values: FormValues): boolean => {
    return (
      !values.security ||
      !values.name ||
      !values.password ||
      !values.email ||
      !values.company
    );
  };

  return (
    <div>
      <H1 bold>
        <FormattedMessage id="login.activateAccess" />
      </H1>
      <SpecialOffer>
        <FormattedMessage
          id="login.activateAccess.subtitle"
          values={{
            sum: (...sum: React.ReactNode[]) => <SumBlock>{sum}</SumBlock>,
            special: (...special: React.ReactNode[]) => (
              <HighlightBlock red>{special}</HighlightBlock>
            ),
            free: (...free: React.ReactNode[]) => (
              <HighlightBlock>{free}</HighlightBlock>
            ),
          }}
        />
      </SpecialOffer>

      <Formik<FormValues>
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
        {({ values }) => {
          return (
            <Form>
              <RowFieldItem>
                <Field name="name">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="login.fullName" />}
                      placeholder={formatMessage({
                        id: "login.fullName.placeholder",
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
                <Field name="company">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="login.companyName" />}
                      placeholder={formatMessage({
                        id: "login.companyName.placeholder",
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
              </RowFieldItem>
              <FieldItem>
                <Field name="email">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="login.yourEmail" />}
                      placeholder={formatMessage({
                        id: "login.yourEmail.placeholder",
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
                      label={<FormattedMessage id="login.password" />}
                      placeholder={formatMessage({
                        id: "login.password.placeholder",
                      })}
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
                      <CheckBoxControl
                        {...field}
                        checked={!!field.value}
                        checkbox
                        label={<FormattedMessage id="login.subscribe" />}
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
                    <CheckBoxControl
                      {...field}
                      checked={!!field.value}
                      checkbox
                      label={
                        <FormattedMessage
                          id="login.security"
                          values={{
                            terms: (...terms: React.ReactNode[]) => (
                              <Link
                                $clear
                                target="_blank"
                                href={config.ui.termsLink}
                                as="a"
                              >
                                {terms}
                              </Link>
                            ),
                            privacy: (...privacy: React.ReactNode[]) => (
                              <Link
                                $clear
                                target="_blank"
                                href={config.ui.privacyLink}
                                as="a"
                              >
                                {privacy}
                              </Link>
                            ),
                          }}
                        />
                      }
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
                  <Button type="submit" disabled={isSignUpDisabled(values)}>
                    <FormattedMessage id="login.signup" />
                  </Button>
                </>
              </BottomBlock>
            </Form>
          );
        }}
      </Formik>
    </div>
  );
};

export default SignupPage;
