import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { Section } from "components/connection/ConnectionForm/Section";
import { ControlLabels } from "components/LabeledControl";
import { FlexContainer } from "components/ui/Flex";
import { Input } from "components/ui/Input";

import styles from "./CreateConnectionNameField.module.scss";

export const CreateConnectionNameField = () => {
  const { formatMessage } = useIntl();

  return (
    <Section title={<FormattedMessage id="connection.title" />}>
      <Field name="name">
        {({ field, meta }: FieldProps<string>) => (
          <FlexContainer alignItems="center">
            <div className={styles.leftFieldCol}>
              <ControlLabels
                nextLine
                error={!!meta.error && meta.touched}
                label={<FormattedMessage id="form.connectionName" />}
                infoTooltipContent={formatMessage({
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
          </FlexContainer>
        )}
      </Field>
    </Section>
  );
};
