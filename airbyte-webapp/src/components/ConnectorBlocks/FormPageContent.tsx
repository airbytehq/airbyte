import styled from "styled-components";

const FormPageContent = styled.div<{ big?: boolean }>`
  // width: 94%;
  // max-width: ${({ big }) => (big ? 1279 : 813)}px;
  // margin: 13px auto;
  padding: 34px 20px 20px 70px;
  display: flex;
  flex-direction: column;
`;

export default FormPageContent;
