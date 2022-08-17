import React, { MutableRefObject } from "react";

export enum ButtonType {
  Primary = "primary",
  Secondary = "secondary",
  Danger = "danger",
  LightGrey = "lightGrey",
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  buttonRef?: MutableRefObject<HTMLButtonElement | null>;
  buttonType?: ButtonType;
  clickable?: boolean;
  customStyles?: string;
  full?: boolean;
  icon?: React.ReactElement;
  iconPosition?: "left" | "right";
  isLoading?: boolean;
  label?: string | React.ReactNode;
  size?: "xs" | "s" | "l";
  wasActive?: boolean;
  width?: number;
}
