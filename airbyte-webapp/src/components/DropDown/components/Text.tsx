import styled from "styled-components";

const Text = styled.div<{ primary?: boolean }>`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  line-height: 20px;
  font-family: ${({ theme }) => theme.regularFont};
  font-style: normal;
  font-weight: normal;
  max-width: 94%;
  color: ${({ theme, primary }) => (primary ? theme.primaryColor : "inhered")};

  .rw-list-option.rw-state-selected & {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

export default Text;
