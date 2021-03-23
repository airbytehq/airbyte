import React from "react";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import TextWithHTML from "components/TextWithHTML";
import { FormBaseItem } from "core/form/types";

type IProps = {
  property: FormBaseItem;
};

const LabelMessage: React.FC<IProps> = ({ property }) => {
  const [, meta] = useField(property.fieldName);

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
};

export { LabelMessage };
