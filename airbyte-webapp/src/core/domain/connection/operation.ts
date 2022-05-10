export interface Operation {
  name: string;
  id?: string;
  workspaceId: string;
  operatorConfiguration: DbtOperationConfiguration | NormalizationOperationConfiguration;
}

export interface Transformation extends Operation {
  operatorConfiguration: DbtOperationConfiguration;
}

export interface DbtOperationConfiguration {
  operatorType: OperatorType.Dbt;
  dbt: DbtConfiguration;
}

export interface Normalization extends Operation {
  operatorType: OperatorType.Normalization;
  operatorConfiguration: NormalizationOperationConfiguration;
}

export interface NormalizationOperationConfiguration {
  operatorType: OperatorType.Normalization;
  normalization: {
    option: NormalizationType;
  };
}

export interface DbtConfiguration {
  gitRepoUrl?: string;
  gitRepoBranch?: string;
  dockerImage: string;
  dbtArguments: string;
}

export enum OperatorType {
  Normalization = "normalization",
  Dbt = "dbt",
}

export enum NormalizationType {
  BASIC = "basic",
  RAW = "raw",
}

export const isDbtTransformation = (op: Operation): op is Transformation => {
  return op.operatorConfiguration.operatorType === OperatorType.Dbt;
};

export const isNormalizationTransformation = (op: Operation): op is Normalization => {
  return op.operatorConfiguration.operatorType === OperatorType.Normalization;
};
