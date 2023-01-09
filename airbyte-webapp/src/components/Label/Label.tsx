import React from "react";
import styled from "styled-components";

interface IProps {
  error?: boolean;
  nextLine?: boolean;
  success?: boolean;
  message?: string | React.ReactNode;
  className?: string;
  onClick?: (data: unknown) => void;
  htmlFor?: string;
}

const Content = styled.label`
  display: block;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.textColor};
  padding-bottom: 5px;

  & a {
    text-decoration: underline;
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const MessageText = styled.span<Pick<IProps, "error" | "success">>`
  white-space: break-spaces;
  color: ${(props) =>
    props.error ? props.theme.dangerColor : props.success ? props.theme.successColor : props.theme.greyColor40};
  font-size: 12px;
  font-weight: 400;

  a:link,
  a:hover,
  a:visited {
    color: ${(props) => props.theme.greyColor40};
  }
`;

const Label: React.FC<React.PropsWithChildren<IProps>> = (props) => (
  <Content className={props.className} onClick={props.onClick} htmlFor={props.htmlFor}>
    {props.children}
    {props.message && (
      <span>
        {props.children ? props.nextLine ? <br /> : " - " : null}
        <MessageText error={props.error}>{props.message}</MessageText>
      </span>
    )}
  </Content>
);

export default Label;
