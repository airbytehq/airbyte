import { H5 } from "components";
import styled from "styled-components";

const Title = styled(H5)`
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 19px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Block = styled.div`
  margin-top: 15 px;
  margin-bottom: 25px;
`;

export { Block, Title };
