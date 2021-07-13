import React from "react";
import { Formik, FieldProps, Field } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import Title from "../components/Title";
import { Form, FieldItem, BottomBlock } from "../components/FormComponents";
import LabeledInput from "components/LabeledInput";
import { Button } from "components/base";
import { Link } from "components/Link";

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
});

const LoginPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  return (
    <div>
      <Title>Sign in to Airbyte</Title>

      <Formik
        initialValues={{
          email: "",
          password: "",
        }}
        validationSchema={LoginPageValidationSchema}
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
                    label={"Password"}
                    placeholder={"ss"}
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
            <BottomBlock>
              <>
                <Link to={"/reset-password"} $light>
                  reset-password
                </Link>
                <Button type="submit">Log In</Button>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default LoginPage;
