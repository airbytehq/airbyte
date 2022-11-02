import { Placement } from "@floating-ui/react-dom";
import React from "react";

export type DisplacementType = 5 | 10; // $spacing-sm, $spacing-md

export type DropdownMenuItemElementType = "a" | "button";

export enum IconPositionType {
  LEFT = "left",
  RIGHT = "right",
}

export interface DropdownMenuOptionType {
  as?: DropdownMenuItemElementType;
  icon?: React.ReactNode;
  iconPosition?: IconPositionType;
  displayName: string;
  value?: any;
  href?: string;
  className?: string;
}

export interface MenuItemContentProps {
  data: DropdownMenuOptionType;
  active?: boolean;
}

export interface DropdownMenuProps {
  options: DropdownMenuOptionType[];
  children: ({ open }: { open: boolean }) => React.ReactNode;
  onChange?: (data: DropdownMenuOptionType) => void;
  placement?: Placement;
  displacement?: DisplacementType;
}
