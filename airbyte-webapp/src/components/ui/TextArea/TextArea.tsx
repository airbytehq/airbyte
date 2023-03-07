import classNames from "classnames";
import React from "react";

import styles from "./TextArea.module.scss";

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
  light?: boolean;
}

export const TextArea: React.FC<React.PropsWithChildren<TextAreaProps>> = ({
  error,
  light,
  children,
  className,
  ...textAreaProps
}) => (
  <textarea
    {...textAreaProps}
    className={classNames(
      styles.textarea,
      {
        [styles.error]: error,
        [styles.light]: light,
      },
      className
    )}
  >
    {children}
  </textarea>
);
