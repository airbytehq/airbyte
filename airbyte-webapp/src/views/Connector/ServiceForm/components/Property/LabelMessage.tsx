import React from "react";
import { FormattedMessage } from "react-intl";

import { TextWithHTML } from "components";

import { FormBaseItem } from "core/form/types";

interface IProps {
  property: FormBaseItem;
  error: string | undefined;
  touched: boolean;
}

const LabelMessage: React.FC<IProps> = ({ property, error, touched }) => {
  const constructExamples = () => {
    if (!property.examples) {
      return null;
    }

    const exampleText = Array.isArray(property.examples) ? property.examples?.join(", ") : property.examples;

    return <FormattedMessage id="form.examples" values={{ examples: exampleText }} />;
  };

  const displayError = !!error && touched;

  const errorMessage =
    displayError && error === "form.pattern.error" ? (
      <FormattedMessage id={error} values={{ pattern: property.pattern }} />
    ) : null;

  const message = property.description ? <TextWithHTML text={property.description} /> : null;

  return (
    <>
      {message} {constructExamples()} {errorMessage}
    </>
  );
};

export { LabelMessage };
