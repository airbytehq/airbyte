import { OperationRead, OperatorDbt } from "../../request/AirbyteClient";

export interface Transformation extends OperationRead {
  operatorConfiguration: DbtOperationConfiguration;
}

export interface DbtOperationConfiguration {
  operatorType: OperatorType.Dbt;
  dbt: DbtConfiguration;
}

export interface Normalization extends OperationRead {
  operatorType: OperatorType.Normalization;
  operatorConfiguration: NormalizationOperationConfiguration;
}

export interface NormalizationOperationConfiguration {
  operatorType: OperatorType.Normalization;
  normalization: {
    option: undefined;
  };
}

export type DbtConfiguration = OperatorDbt;

export enum OperatorType {
  Normalization = "normalization",
  Dbt = "dbt",
}

export enum NormalizationType {
  BASIC = "basic",
  RAW = "raw",
}

export const isDbtTransformation = (op: OperationRead): op is Transformation => {
  return op.operatorConfiguration.operatorType === OperatorType.Dbt;
};

export const isNormalizationTransformation = (op: OperationRead): op is Normalization => {
  return op.operatorConfiguration.operatorType === OperatorType.Normalization;
};
