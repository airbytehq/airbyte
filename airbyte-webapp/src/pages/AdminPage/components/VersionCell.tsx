import React from "react";
import { Formik, Form, FieldProps, Field } from "formik";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Input from "../../../components/Input";
import Button from "../../../components/Button";

type IProps = {
  version?: string;
  empty?: boolean;
};

const FormContent = styled.div`
  width: 270px;
  margin: -10px 0;
`;

const VersionInput = styled(Input)`
  max-width: 145px;
  margin-right: 19px;
`;

const VersionCell: React.FC<IProps> = ({ version, empty }) => {
  if (empty) {
    return <FormContent />;
  }

  return (
    <FormContent>
      <Formik
        initialValues={{
          version
        }}
        onSubmit={(values, { setSubmitting }) => {
          // TODO: add real change action
          console.log(values);
          setSubmitting(false);
        }}
      >
        {({ isSubmitting, dirty }) => (
          <Form>
            <Field name="version">
              {({ field }: FieldProps<string>) => (
                <VersionInput {...field} type="text" autoComplete="off" />
              )}
            </Field>
            <Button type="submit" disabled={isSubmitting || !dirty}>
              <FormattedMessage id="form.change" />
            </Button>
          </Form>
        )}
      </Formik>
    </FormContent>
  );
};

export default VersionCell;
