import styled from "styled-components";

interface IProps {
  center?: boolean;
  bold?: boolean;
  parentColor?: boolean;
  highlighted?: boolean;
}

export const H1 = styled.h1<IProps>`
  font-size: ${({ theme }) => theme.h1?.fontSize || "28px"};
  line-height: ${({ theme }) => theme.h1?.lineHeight || "34px"};
  font-style: normal;
  font-weight: ${(props) => (props.bold ? "bold" : 500)};
  display: block;
  text-align: ${(props) => (props.center ? "center" : "left")};
  color: ${({ theme, parentColor, highlighted }) =>
    parentColor ? "inherit" : highlighted ? theme.redColor : theme.textColor};
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
  font-size: ${({ theme }) => theme.h5?.fontSize || "16px"};
  line-height: ${({ theme }) => theme.h5?.lineHeight || "28px"};
`;

export const H6 = styled(H1).attrs({ as: "h6" })`
  font-size: ${({ theme }) => theme.h5?.fontSize || "14px"};
  line-height: ${({ theme }) => theme.h5?.lineHeight || "17px"};
`;
