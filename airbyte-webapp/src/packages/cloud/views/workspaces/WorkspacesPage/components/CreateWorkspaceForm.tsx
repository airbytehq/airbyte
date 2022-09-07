import { Field, FieldProps, Formik, Form } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LoadingButton, Input } from "components";

interface CreateWorkspaceFormProps {
  onSubmit: (values: { name: string }) => Promise<void>;
}

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
    border-bottom: ${({ error, theme }) => (error ? `${theme.dangerColor} 1px solid` : "none")};
    padding: 0 0 2px;
  }
`;

const CreateWorkspaceForm: React.FC<CreateWorkspaceFormProps> = ({ onSubmit }) => {
  return (
    <Formik
      initialValues={{
        name: "",
      }}
      validationSchema={CreateWorkspaceFormValidationSchema}
      onSubmit={onSubmit}
      validateOnBlur
    >
      {({ isSubmitting }) => (
        <CreationForm>
          <Field name="name">
            {({ field, meta }: FieldProps<string>) => (
              <ClearInput {...field} type="text" error={!!meta.error && meta.touched} />
            )}
          </Field>
          <LoadingButton type="submit" isLoading={isSubmitting} data-testid="workspaces.create">
            <FormattedMessage id="workspaces.create" />
          </LoadingButton>
        </CreationForm>
      )}
    </Formik>
  );
};

export default CreateWorkspaceForm;
