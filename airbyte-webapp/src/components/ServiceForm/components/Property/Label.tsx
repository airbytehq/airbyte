import React, { useMemo } from "react";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import TextWithHTML from "components/TextWithHTML";
import { ControlLabels } from "components/LabeledControl";
import { FormBaseItem } from "core/form/types";

type IProps = {
  property: FormBaseItem;
};

const Label: React.FC<IProps> = ({ property, children }) => {
  const [, meta] = useField(property.fieldName);

  const label = `${property.title || property.fieldKey}${
    property.isRequired ? " *" : ""
  }`;

  const displayError = !!meta.error && meta.touched;

  const constructMessage = useMemo(() => {
    const errorMessage =
      displayError && meta.error === "form.pattern.error" ? (
        <FormattedMessage
          id={meta.error}
          values={{ pattern: property.pattern }}
        />
      ) : null;

    const message = property.description ? (
      <TextWithHTML text={property.description} />
    ) : null;

    return (
      <>
        {message} {errorMessage}
      </>
    );
  }, [displayError, meta.error, property.description, property.pattern]);

  return (
    <ControlLabels
      error={displayError}
      label={label}
      message={constructMessage}
    >
      {children}
    </ControlLabels>
  );
};

export { Label };
