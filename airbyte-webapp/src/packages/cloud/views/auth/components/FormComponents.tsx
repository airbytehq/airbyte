import { Form as FormikForm } from "formik";
import styled from "styled-components";

export const Form = styled(FormikForm)`
  margin-top: 42px;
`;

export const FieldItem = styled.div`
  margin-bottom: 21px;
`;

export const RowFieldItem = styled(FieldItem)`
  display: flex;
  flex-direction: row;

  & > div {
    flex: 1 0 0;
    margin-right: 14px;

    &:last-child {
      margin-right: 0;
    }
  }
`;

export const BottomBlock = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top: 38px;
  font-size: 11px;
`;

export const BottomBlockStatusMessage = styled.div`
  max-width: calc(100% - 100px);
  color: ${(props) => props.theme.dangerColor};
`;
