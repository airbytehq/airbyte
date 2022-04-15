import React from "react";
import DOMPurify from "dompurify";

type IProps = {
  text?: string;
};

const TextWithHTML: React.FC<IProps> = ({ text }) => {
  if (!text) {
    return null;
  }

  DOMPurify.addHook("afterSanitizeAttributes", function (node) {
    if ("rel" in node) {
      node.setAttribute("target", "_blank");
      node.setAttribute("rel", "noopener noreferrer");
    }
  });

  var sanitizedHtmlText = DOMPurify.sanitize(text, { ALLOWED_TAGS: ["a"], ALLOWED_ATTR: ["rel"] });

  return <span dangerouslySetInnerHTML={{ __html: sanitizedHtmlText }} />;
};

export default TextWithHTML;
