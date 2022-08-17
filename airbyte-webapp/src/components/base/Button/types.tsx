import React from "react";

export enum ButtonType {
  Primary = "primary",
  Secondary = "secondary",
  Danger = "danger",
  LightGrey = "lightGrey",
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  customStyles?: string;
  buttonType?: ButtonType;
  clickable?: boolean;
  full?: boolean;
  icon?: React.ReactElement;
  iconPosition?: "left" | "right";
  isLoading?: boolean;
  label?: string | React.ReactNode;
  size?: "xs" | "s" | "l";
  wasActive?: boolean;
  width?: number;
}
