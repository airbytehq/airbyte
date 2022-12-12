import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { Input } from "components/ui/Input";

import { Section } from "views/Connection/ConnectionForm/components/Section";

import styles from "./CreateConnectionNameField.module.scss";

export const CreateConnectionNameField = () => {
  const { formatMessage } = useIntl();

  return (
    <Section title={<FormattedMessage id="connection.title" />}>
      <Field name="name">
        {({ field, meta }: FieldProps<string>) => (
          <div className={styles.flexRow}>
            <div className={styles.leftFieldCol}>
              <ControlLabels
                nextLine
                error={!!meta.error && meta.touched}
                label={<FormattedMessage id="form.connectionName" />}
                message={formatMessage({
                  id: "form.connectionName.message",
                })}
              />
            </div>
            <div className={styles.rightFieldCol}>
              <Input
                {...field}
                error={!!meta.error}
                data-testid="connectionName"
                placeholder={formatMessage({
                  id: "form.connectionName.placeholder",
                })}
              />
            </div>
          </div>
        )}
      </Field>
    </Section>
  );
};
