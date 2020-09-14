import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";
import JobLogsResource from "./JobLogs";

export interface Job {
  id: number;
  configType: string;
  configId: string;
  createdAt: number;
  startedAt: number;
  updatedAt: number;
  status: string;
}

export default class JobResource extends BaseResource implements Job {
  readonly id: number = 0;
  readonly configType: string = "";
  readonly configId: string = "";
  readonly createdAt: number = 0;
  readonly startedAt: number = 0;
  readonly updatedAt: number = 0;
  readonly status: string = "";

  pk() {
    return this.id?.toString();
  }

  static urlRoot = "jobs";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { jobs: [this.asSchema()] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: {
        job: this.asSchema(),
        logs: JobLogsResource.asSchema()
      }
    };
  }
}
