import React from "react";
import { Formik, Form, FieldProps, Field } from "formik";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Input from "../../../components/Input";
import Button from "../../../components/Button";
import Spinner from "../../../components/Spinner";
import { FormContent } from "./PageComponents";

type IProps = {
  version: string;
  id: string;
  onChange: ({ version, id }: { version: string; id: string }) => void;
  feedback?: "success" | string;
};

const VersionInput = styled(Input)`
  max-width: 145px;
  margin-right: 19px;
`;

const SuccessMessage = styled.div`
  color: ${({ theme }) => theme.successColor};
  font-size: 12px;
  line-height: 18px;
  position: absolute;
  text-align: right;
  width: 205px;
  left: -218px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  white-space: break-spaces;
`;

const ErrorMessage = styled(SuccessMessage)`
  color: ${({ theme }) => theme.dangerColor};
  font-size: 11px;
  line-height: 14px;
`;

const VersionCell: React.FC<IProps> = ({ version, id, onChange, feedback }) => {
  const renderFeedback = (
    dirty: boolean,
    isSubmitting: boolean,
    feedback?: string
  ) => {
    if (isSubmitting) {
      return (
        <SuccessMessage>
          <Spinner small />
        </SuccessMessage>
      );
    }

    if (feedback && !dirty) {
      if (feedback === "success") {
        return (
          <SuccessMessage>
            <FormattedMessage id="form.savedChange" />
          </SuccessMessage>
        );
      } else {
        return <ErrorMessage>{feedback}</ErrorMessage>;
      }
    }

    return null;
  };

  return (
    <FormContent>
      <Formik
        initialValues={{
          version,
        }}
        onSubmit={async (values, { setSubmitting }) => {
          await onChange({ id, version: values.version });
          setSubmitting(false);
        }}
      >
        {({ isSubmitting, dirty }) => (
          <Form>
            {renderFeedback(dirty, isSubmitting, feedback)}
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
