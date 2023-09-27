import styled from "styled-components";

const FormPageContent = styled.div<{ big?: boolean }>`
  padding: 34px 20px 100px 70px;
  display: flex;
  flex-direction: column;
`;

const ConnectionFormPageContent = styled.div<{ big?: boolean }>`
  padding: 34px 0px 0px 0px;
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const FormContainer = styled.div`
  margin: 18px auto;
  padding: 0 20px 70px 0;
  box-sizing: border-box;
`;
export { FormPageContent, ConnectionFormPageContent, FormContainer };
