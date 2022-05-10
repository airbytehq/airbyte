import { OperationRead, OperatorDbt, OperatorNormalization, OperatorType } from "../../request/AirbyteClient";

export interface Transformation extends OperationRead {
  operatorConfiguration: DbtOperationConfiguration;
}

export interface DbtOperationConfiguration {
  operatorType: typeof OperatorType.dbt;
  dbt: OperatorDbt;
}

export interface Normalization extends OperationRead {
  operatorConfiguration: NormalizationOperationConfiguration;
}

export interface NormalizationOperationConfiguration {
  operatorType: typeof OperatorType.normalization;
  normalization: OperatorNormalization;
}

export enum NormalizationType {
  basic = "basic",
  raw = "raw",
}

export const isDbtTransformation = (op: OperationRead): op is Transformation => {
  return op.operatorConfiguration.operatorType === OperatorType.dbt;
};

export const isNormalizationTransformation = (op: OperationRead): op is Normalization => {
  return op.operatorConfiguration.operatorType === OperatorType.normalization;
};
