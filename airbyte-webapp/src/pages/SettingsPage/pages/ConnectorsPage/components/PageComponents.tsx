import styled from "styled-components";

import { H5 } from "components/base/Titles";

const Title = styled(H5)`
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 19px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Block = styled.div`
  margin-bottom: 56px;
`;

const FormContent = styled.div`
  width: 253px;
  margin: -10px 0 -10px 200px;
  position: relative;
`;

export { Title, Block, FormContent };
