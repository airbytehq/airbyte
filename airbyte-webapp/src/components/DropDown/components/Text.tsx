import styled from "styled-components";

const Text = styled.div`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  line-height: 20px;
  font-family: ${({ theme }) => theme.regularFont};
  font-style: normal;
  font-weight: normal;
  max-width: 94%;

  .rw-list-option.rw-state-selected & {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

export default Text;
