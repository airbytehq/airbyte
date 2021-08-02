import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Formik, Form } from "formik";
import * as yup from "yup";

import { Button, Input } from "components";

type CreateWorkspaceFormProps = {
  onSubmit: ({ name }: { name: string }) => void;
};

const CreateWorkspaceFormValidationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
});

const CreationForm = styled(Form)`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ClearInput = styled(Input)`
  flex: 1 0 0;
  margin-right: 10px;

  &,
  &:hover,
  &:focus {
    background: ${({ theme }) => theme.whiteColor};
    border: none;
    border-radius: 0;
    border-bottom: ${({ error, theme }) =>
      error ? `${theme.dangerColor} 1px solid` : "none"};
    padding: 0 0 2px;
  }
`;

const CreateWorkspaceForm: React.FC<CreateWorkspaceFormProps> = ({
  onSubmit,
}) => {
  return (
    <Formik
      initialValues={{
        name: "",
      }}
      validationSchema={CreateWorkspaceFormValidationSchema}
      onSubmit={(values) => onSubmit(values)}
      validateOnBlur={true}
    >
      {() => (
        <CreationForm>
          <Field name="name">
            {({ field, meta }: FieldProps<string>) => (
              <ClearInput
                {...field}
                autoFocus
                type="text"
                error={!!meta.error && meta.touched}
              />
            )}
          </Field>
          <Button type="submit">
            <FormattedMessage id="workspaces.create" />
          </Button>
        </CreationForm>
      )}
    </Formik>
  );
};

export default CreateWorkspaceForm;
