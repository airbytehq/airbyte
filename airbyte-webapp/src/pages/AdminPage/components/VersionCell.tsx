import React from "react";
import { Formik, Form, FieldProps, Field } from "formik";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Input from "../../../components/Input";
import Button from "../../../components/Button";
import { FormContent } from "./PageComponents";

type IProps = {
  version: string;
  id: string;
  onChange: ({ version, id }: { version: string; id: string }) => void;
};

const VersionInput = styled(Input)`
  max-width: 145px;
  margin-right: 19px;
`;

const VersionCell: React.FC<IProps> = ({ version, id, onChange }) => {
  return (
    <FormContent>
      <Formik
        initialValues={{
          version
        }}
        onSubmit={async (values, { setSubmitting }) => {
          await onChange({ id, version: values.version });
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
