import styled from "styled-components";

import { Link as ReactLink } from "react-router-dom";

export type ILinkProps = {
  bold?: boolean;
  clear?: boolean;
};

const Link = styled(ReactLink)<ILinkProps>`
  color: ${({ theme }) => theme.primaryColor};

  font-weight: ${({ bold }) => (bold ? "bold" : "normal")};
  text-decoration: ${({ clear }) => (clear ? "none" : "underline")};

  &:hover {
    opacity: 0.8;
  }
`;

export default Link;
