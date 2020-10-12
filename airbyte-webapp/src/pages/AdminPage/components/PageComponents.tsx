import styled from "styled-components";
import { H5 } from "../../../components/Titles";

const Title = styled(H5)`
  color: ${({ theme }) => theme.darkPrimaryColor};
  margin-bottom: 19px;
`;

const Block = styled.div`
  margin-bottom: 56px;
`;

const FormContent = styled.div`
  width: 270px;
  margin: -10px 0 -10px 118px;
  position: relative;
`;

const FormContentTitle = styled(FormContent)`
  margin: 0 0 0 118px;
`;

export { Title, Block, FormContent, FormContentTitle };
