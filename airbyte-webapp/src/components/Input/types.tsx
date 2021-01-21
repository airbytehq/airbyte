import React from "react";

export type InputProps = {
  error?: boolean;
  light?: boolean;
  withEditButton?: boolean;
  setValue?: (value: string) => void;
} & React.InputHTMLAttributes<HTMLInputElement>;
