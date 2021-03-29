import React from "react";
import { FormattedHTMLMessage } from "react-intl";
import sanitizeHtml from "sanitize-html";

type IProps = {
  text?: string;
};

const TextWithHTML: React.FC<IProps> = ({ text }) => {
  if (!text) {
    return null;
  }

  const sanitizedHtmlText = sanitizeHtml(text, {
    transformTags: {
      a: sanitizeHtml.simpleTransform("a", { target: "_blank" }),
    },
  });

  return (
    <FormattedHTMLMessage
      id="textWithHtmlTags"
      defaultMessage={sanitizedHtmlText}
    />
  );
};

export default TextWithHTML;
