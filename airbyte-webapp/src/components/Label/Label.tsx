import React from "react";
import styled from "styled-components";

interface IProps {
  error?: boolean;
  nextLine?: boolean;
  success?: boolean;
  message?: string | React.ReactNode;
  additionLength?: number;
  className?: string;
  onClick?: (data: unknown) => void;
}

const Content = styled.label<{ additionLength?: number | string }>`
  display: block;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.textColor};
  padding-bottom: 5px;
  width: calc(100% + ${({ additionLength }) => (additionLength === 0 || additionLength ? additionLength : 30)}px);

  & a {
    text-decoration: underline;
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const MessageText = styled.span<Pick<IProps, "error" | "success">>`
  white-space: break-spaces;
  color: ${(props) =>
    props.error ? props.theme.dangerColor : props.success ? props.theme.successColor : props.theme.greyColor40};
  font-size: 13px;
`;

const Label: React.FC<IProps> = (props) => (
  <Content additionLength={props.additionLength} className={props.className} onClick={props.onClick}>
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
