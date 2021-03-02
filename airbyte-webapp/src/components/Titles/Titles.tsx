import styled from "styled-components";

type IProps = {
  center?: boolean;
  bold?: boolean;
};

export const H1 = styled.h1<IProps>`
  font-style: normal;
  font-weight: ${(props) => (props.bold ? 600 : 500)};
  font-size: 28px;
  line-height: 34px;
  display: block;
  text-align: ${(props) => (props.center ? "center" : "left")};
  color: ${({ theme }) => theme.textColor};
  margin: 0;
`;

export const H2 = styled(H1).attrs({ as: "h2" })`
  font-size: 26px;
  line-height: 32px;
`;

export const H3 = styled(H1).attrs({ as: "h3" })`
  font-size: 20px;
  line-height: 24px;
`;

export const H4 = styled(H1).attrs({ as: "h4" })`
  font-size: 18px;
  line-height: 22px;
`;

export const H5 = styled(H1).attrs({ as: "h5" })`
  font-size: 15px;
  line-height: 18px;
`;
