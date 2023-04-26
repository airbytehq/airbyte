import {
  Link as ReactLink,
  // LinkProps as ReactLinkProps,
} from "react-router-dom";
import styled from "styled-components";

export interface ILinkProps {
  bold?: boolean;
  $clear?: boolean;
  $light?: boolean;
  medium?: boolean;
}

const getFontWeight = (props: ILinkProps) => {
  if (props.bold) {
    return "bold";
  }
  if (props.medium) {
    return "500";
  }
  return "normal";
};

// TODO: fix typings
const Link = styled(ReactLink)<ILinkProps /* & ReactLinkProps */>`
  color: ${({ theme, $light }) => ($light ? theme.darkGreyColor : theme.primaryColor)};

  // font-weight: ${(props) => getFontWeight(props)};
  text-decoration: ${({ $clear }) => ($clear ? "none" : "underline")};

  &:hover {
    opacity: 0.8;
  }
`;

export default Link;
