import { Resource, FetchOptions } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface JobItem {
  id: number;
  configType: string;
  configId: string;
  createdAt: number;
  startedAt: number;
  updatedAt: number;
  status: string;
}

export interface Logs {
  logLines: string[];
}

export interface Attempt {
  id: number;
  status: string;
  createdAt: number;
  updatedAt: number;
  endedAt: number;
  bytesSynced: number;
  recordsSynced: number;
}

export interface Job {
  job: JobItem;
  logsByAttempt: { [key: string]: Logs };
  attempts: Attempt[];
}

export default class JobResource extends BaseResource implements Job {
  readonly job: JobItem = {
    id: 0,
    configType: "",
    configId: "",
    createdAt: 0,
    startedAt: 0,
    updatedAt: 0,
    status: ""
  };
  readonly attempts: Attempt[] = [];
  readonly logsByAttempt: { [key: string]: Logs } = {};

  pk() {
    return this.job?.id?.toString();
  }

  static urlRoot = "jobs";

  static getFetchOptions(): FetchOptions {
    return {
      pollFrequency: 2500 // every 2,5 seconds
    };
  }

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      fetch: async (params: any): Promise<any> => {
        const jobsResult = await this.fetch(
          "post",
          `${this.listUrl(params)}/list`,
          { ...params }
        );

        return {
          jobs: jobsResult.jobs
        };
      },
      schema: { jobs: [this] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const jobResult = await this.fetch(
          "post",
          `${this.url(params)}/get`,
          params
        );

        const attemptsValue = jobResult.attempts.map(
          (attemptItem: any) => attemptItem.attempt
        );

        return {
          job: jobResult.job,
          attempts: attemptsValue,
          logsByAttempt: Object.fromEntries(
            jobResult.attempts.map((attemptItem: any) => [
              attemptItem.attempt.id,
              attemptItem.logs
            ])
          )
        };
      },
      schema: this
    };
  }
}
