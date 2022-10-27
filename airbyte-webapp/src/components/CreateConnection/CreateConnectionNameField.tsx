import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { Heading } from "components/ui/Heading";
import { Input } from "components/ui/Input";

import { Section } from "views/Connection/ConnectionForm/components/Section";

import styles from "./CreateConnectionNameField.module.scss";

export const CreateConnectionNameField = () => {
  const { formatMessage } = useIntl();

  return (
    <Section>
      <Field name="name">
        {({ field, meta }: FieldProps<string>) => (
          <div className={styles.flexRow}>
            <div className={styles.leftFieldCol}>
              <ControlLabels
                className={styles.connectionLabel}
                nextLine
                error={!!meta.error && meta.touched}
                label={
                  <Heading as="h5" className={styles.labelHeading}>
                    <FormattedMessage id="form.connectionName" />
                  </Heading>
                }
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
