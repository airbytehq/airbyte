import React from "react";
import styled from "styled-components";

interface IProps {
  email: string;
  subject: string;
  body: string;
  children: React.ReactNode;
}

const A = styled.a`
  text-decoration: none;
`;

export const Mailto: React.FC<IProps> = ({ email, subject, body, children }) => {
  return (
    <A href={`mailto:${email}?subject=${encodeURIComponent(subject) || ""}&body=${encodeURIComponent(body) || ""}`}>
      {children}
    </A>
  );
};
