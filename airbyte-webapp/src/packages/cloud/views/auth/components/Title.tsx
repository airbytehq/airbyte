import styled from "styled-components";

const Title = styled.h1`
  font-style: normal;
  font-weight: bold;
  font-size: 24px;
  line-height: 29px;
  color: ${({ theme }) => theme.redColor};
  margin: 0;
`;

export default Title;
