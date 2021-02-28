import React, { useMemo } from "react";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import TextWithHTML from "../../../TextWithHTML";
import { ControlLabels } from "../../../LabeledControl";
import { FormBaseItem } from "../../../../core/form/types";

type IProps = {
  property: FormBaseItem;
};

const Label: React.FC<IProps> = ({ property, children }) => {
  const [, meta] = useField(property.fieldName);

  const label = `${property.title || property.fieldKey}${
    property.isRequired ? " *" : ""
  }`;

  const constructExamples = () => {
    if (!property.examples) {
      return null;
    }

    const exampleText = Array.isArray(property.examples)
      ? property.examples?.join(", ")
      : property.examples;

    return (
      <FormattedMessage id="form.examples" values={{ examples: exampleText }} />
    );
  };

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
        {message} {constructExamples()} {errorMessage}
      </>
    );
  }, [
    constructExamples,
    displayError,
    meta.error,
    property.description,
    property.pattern
  ]);

  return (
    <ControlLabels
      labelAdditionLength={0}
      error={displayError}
      label={label}
      message={constructMessage}
    >
      {children}
    </ControlLabels>
  );
};

export { Label };
