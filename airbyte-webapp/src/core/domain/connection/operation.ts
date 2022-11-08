import { OperationCreate, OperationRead, OperatorType } from "../../request/AirbyteClient";

export enum NormalizationType {
  basic = "basic",
  raw = "raw",
}

export const isDbtTransformation = (op: OperationCreate): op is OperationRead => {
  return op.operatorConfiguration.operatorType === OperatorType.dbt;
};

export const isNormalizationTransformation = (op: OperationCreate): op is OperationRead => {
  return op.operatorConfiguration.operatorType === OperatorType.normalization;
};
