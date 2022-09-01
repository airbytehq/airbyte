import React from "react";
import sanitizeHtml from "sanitize-html";

interface IProps extends React.InputHTMLAttributes<HTMLInputElement> {
  text?: string;
}

const allowedAttributes = {
  ...sanitizeHtml.defaults.allowedAttributes,
  a: [...sanitizeHtml.defaults.allowedAttributes["a"], "rel"],
};

const TextWithHTML: React.FC<IProps> = ({ text, className }) => {
  if (!text) {
    return null;
  }

  const sanitizedHtmlText = sanitizeHtml(text, {
    allowedAttributes,
    transformTags: {
      a: sanitizeHtml.simpleTransform("a", {
        target: "_blank",
        rel: "noopener noreferrer",
      }),
    },
  });

  return <span className={className} dangerouslySetInnerHTML={{ __html: sanitizedHtmlText }} />;
};

export default TextWithHTML;
