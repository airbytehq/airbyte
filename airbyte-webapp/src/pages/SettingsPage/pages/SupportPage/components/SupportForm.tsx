import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LoadingButton, TextArea, DropDown, DropDownRow } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";

import { useUniqueFormId } from "hooks/services/FormChangeTracker";
import { FieldItem, Form } from "pages/AuthPage/components/FormComponents";

import styles from "./SupportForm.module.scss";
import { QuestionType } from "./type";

const validationSchema = yup.object().shape({
  type: yup.string().required("settings.support.select.label"),
  description: yup.string().required("settings.support.textarea.placeholder"),
});

export interface SupportFormValues {
  type: string;
  description: string;
}

interface SupportFormProps {
  onSubmit: (value: SupportFormValues) => void;
}

const SupportForm: React.FC<SupportFormProps> = ({ onSubmit }) => {
  const { formatMessage } = useIntl();
  const formId = useUniqueFormId();

  const initialValues: SupportFormValues = {
    type: "",
    description: "",
  };

  const supportOptions: DropDownRow.IDataItem[] = [
    {
      label: formatMessage({ id: "settings.support.select.option.planBilling" }),
      value: QuestionType.PLAN_BILLING,
    },
    {
      label: formatMessage({ id: "settings.support.select.option.technicalSupport" }),
      value: QuestionType.TECHNICAL_SUPPORT,
    },
    {
      label: formatMessage({ id: "settings.support.select.option.accountRelated" }),
      value: QuestionType.ACCOUNT_RELATED,
    },
    {
      label: formatMessage({ id: "settings.support.select.option.other" }),
      value: QuestionType.OTHER,
    },
  ];

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onSubmit}
      validateOnBlur
      validateOnChange
    >
      {({ isValid, dirty, isSubmitting, setFieldValue }) => (
        <Form top="0">
          <FormChangeTracker changed={dirty} formId={formId} />
          <FieldItem bottom="50">
            <div className={styles.formItemLabel}>
              <FormattedMessage id="settings.support.select.label" />
            </div>
            <Field name="type">
              {({ field }: FieldProps<string>) => (
                <DropDown
                  $background="white"
                  $withBorder
                  placeholder=""
                  {...field}
                  options={supportOptions}
                  onChange={(selectedItem) => selectedItem && setFieldValue("type", selectedItem.value)}
                />
              )}
            </Field>
          </FieldItem>

          <FieldItem bottom="50">
            <div className={styles.formItemLabel}>
              <FormattedMessage id="settings.support.textarea.label" />
            </div>
            <Field name="description">
              {({ field, meta }: FieldProps<string>) => (
                <TextArea
                  {...field}
                  error={!!meta.error && meta.touched}
                  className={styles.textarea}
                  placeholder={formatMessage({ id: "settings.support.textarea.placeholder" })}
                />
              )}
            </Field>
          </FieldItem>

          <div className={styles.buttonContainer}>
            <LoadingButton white disabled={!(isValid && dirty)} size="xl" type="submit" isLoading={isSubmitting}>
              <FormattedMessage id="settings.support.form.button" />
            </LoadingButton>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default SupportForm;
