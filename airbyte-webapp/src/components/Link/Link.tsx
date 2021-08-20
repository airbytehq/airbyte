import styled from "styled-components";

import {
  Link as ReactLink,
  // LinkProps as ReactLinkProps,
} from "react-router-dom";

export type ILinkProps = {
  bold?: boolean;
  $clear?: boolean;
  $light?: boolean;
};

// TODO: fix typings
const Link = styled(ReactLink)<ILinkProps /*& ReactLinkProps */>`
  color: ${({ theme, $light }) =>
    $light ? theme.darkGreyColor : theme.primaryColor};

  font-weight: ${({ bold }) => (bold ? "bold" : "normal")};
  text-decoration: ${({ $clear }) => ($clear ? "none" : "underline")};

  &:hover {
    opacity: 0.8;
  }
`;

export default Link;
