import {
  // eslint-disable-next-line no-restricted-imports
  Link as ReactLink,
  // LinkProps as ReactLinkProps,
} from "react-router-dom";
import styled from "styled-components";

export interface LinkProps {
  bold?: boolean;
  $clear?: boolean;
  $light?: boolean;
}

/** @deprecated Use components/ui/Link instead */
export const Link = styled(ReactLink)<LinkProps /* & ReactLinkProps */>`
  color: ${({ theme, $light }) => ($light ? theme.darkGreyColor : theme.primaryColor)};

  font-weight: ${({ bold }) => (bold ? "bold" : "normal")};
  text-decoration: ${({ $clear }) => ($clear ? "none" : "underline")};

  &:hover {
    opacity: 0.8;
  }
`;
