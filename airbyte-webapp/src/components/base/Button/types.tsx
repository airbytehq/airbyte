import React from "react";

type ButtonSize = "xs" | "sm" | "lg";
type ButtonVariant = "primary" | "secondary" | "danger" | "light";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  customStyle?: string;
  variant?: ButtonVariant;
  clickable?: boolean;
  full?: boolean;
  icon?: React.ReactElement;
  iconPosition?: "left" | "right";
  isLoading?: boolean;
  size?: ButtonSize;
  wasActive?: boolean;
  width?: number;
}
