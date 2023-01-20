import styled from "styled-components";

import { H5 } from "components/base/Titles";

export const Title = styled(H5)`
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 19px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const Block = styled.div`
  margin-bottom: 56px;
`;

export const FormContent = styled.div`
  width: 253px;
  margin: -10px 0 -10px 200px;
  position: relative;
`;

export const FormContentTitle = styled(FormContent)`
  margin: 0 0 0 200px;
`;
