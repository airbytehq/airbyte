import React from "react";
import { Field, FieldProps, Formik } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { Button, LabeledInput, Link } from "components";
import { FormTitle } from "../components/FormTitle";
import { Routes } from "../../../routes";

const ResetPasswordPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const ResetPasswordPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  return (
    <div>
      <FormTitle bold>
        <FormattedMessage id="login.resetPassword" />
      </FormTitle>

      <Formik
        initialValues={{
          email: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={() => console.log("ok")}
        validateOnBlur={true}
        validateOnChange={false}
      >
        {() => (
          <Form>
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
            <BottomBlock>
              <>
                <Link to={Routes.Login} $light>
                  <FormattedMessage id="login.backLogin" />
                </Link>
                <Button type="submit">
                  <FormattedMessage id="login.resetPassword" />
                </Button>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default ResetPasswordPage;
