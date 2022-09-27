import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { Input } from "components/base";
import { Text } from "components/base/Text";
import { ControlLabels } from "components/LabeledControl";

import { Section } from "views/Connection/ConnectionForm/components/Section";

import styles from "./CreateConnectionName.module.scss";

export const CreateConnectionName = () => {
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
                  <Text as="h5" className={styles.labelHeading}>
                    <FormattedMessage id="form.connectionName" />
                  </Text>
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
