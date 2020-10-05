import styled from "styled-components";
import { H5 } from "../../../components/Titles";

const Title = styled(H5)`
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 19px;
`;

const Block = styled.div`
  margin-bottom: 56px;
`;

export { Title, Block };
