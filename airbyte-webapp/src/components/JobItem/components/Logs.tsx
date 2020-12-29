import styled from "styled-components";

const Logs = styled.div`
  padding: 11px 42px 20px;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  font-family: ${({ theme }) => theme.codeFont};
  word-wrap: break-word;
`;

export default Logs;
