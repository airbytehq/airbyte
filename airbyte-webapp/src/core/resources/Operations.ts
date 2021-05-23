import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Normalization {
  option: string;
}

export interface Dbt {
  gitRepoUrl: string;
  gitRepoBranch: string;
  dockerImage: string;
  dbtArguments: string;
}

export interface OperationConfiguration {
  operatorType: string;
  normalization: Normalization;
  dbt: Dbt;
}

export interface Operation {
  operationId: string;
  name: string;
  operatorConfiguration: OperationConfiguration;
}

export default class OperationResource
  extends BaseResource
  implements Operation {
  readonly operationId: string = "";
  readonly name: string = "";
  readonly operatorConfiguration: OperationConfiguration = {
    operatorType: "",
    normalization: {
      option: "",
    },
    dbt: {
      gitRepoUrl: "",
      gitRepoBranch: "",
      dockerImage: "",
      dbtArguments: "",
    },
  };

  pk(): string {
    return this.operationId?.toString();
  }

  static urlRoot = "operations";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Operation[]>> {
    return {
      ...super.listShape(),
      schema: { operations: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Operation>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Operation>> {
    return {
      ...super.partialUpdateShape(),
      schema: this,
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Operation>> {
    return {
      ...super.createShape(),
      schema: this,
    };
  }
}
