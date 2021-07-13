import styled from "styled-components";

type IProps = {
  center?: boolean;
  bold?: boolean;
  danger?: boolean;
};

export const H1 = styled.h1<IProps>`
  font-style: normal;
  font-weight: ${(props) => (props.bold ? 600 : 500)};
  font-size: 24px;
  line-height: 29px;
  display: block;
  text-align: ${(props) => (props.center ? "center" : "left")};
  color: ${({ theme, danger }) => (danger ? theme.redColor : theme.textColor)};
  margin: 0;
`;

export const H2 = styled(H1).attrs({ as: "h2" })`
  font-size: 22px;
  line-height: 27px;
`;

export const H3 = styled(H1).attrs({ as: "h3" })`
  font-size: 18px;
  line-height: 22px;
`;

export const H4 = styled(H1).attrs({ as: "h3" })`
  font-size: 16px;
  line-height: 28px;
  font-weight: ${(props) => (props.bold ? 500 : "normal")};
`;
