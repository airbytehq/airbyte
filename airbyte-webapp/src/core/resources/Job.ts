import {
  FetchOptions,
  MutateShape,
  ReadShape,
  Resource,
  SchemaDetail,
} from "rest-hooks";
import BaseResource from "./BaseResource";
import Status from "../statuses";

export interface JobItem {
  id: number | string;
  configType: string;
  configId: string;
  createdAt: number;
  startedAt: number;
  updatedAt: number;
  status: Status | null;
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
    status: null,
  };
  readonly attempts: Attempt[] = [];
  readonly logsByAttempt: { [key: string]: Logs } = {};

  pk(): string {
    return this.job?.id?.toString();
  }

  static urlRoot = "jobs";

  static getFetchOptions(): FetchOptions {
    return {
      pollFrequency: 2500, // every 2,5 seconds
    };
  }

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<{ jobs: Job[] }>> {
    return {
      ...super.listShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<{ jobs: Job[] }> => {
        const jobsResult = await this.fetch(
          "post",
          `${this.listUrl(params)}/list`,
          { ...params }
        );

        return {
          jobs: jobsResult.jobs,
        };
      },
      schema: { jobs: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Job>> {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<Job> => {
        const jobResult: {
          job: JobItem;
          attempts: { attempt: Attempt; logs: Logs }[];
        } = await this.fetch("post", `${this.url(params)}/get`, params);

        const attemptsValue = jobResult.attempts.map(
          (attemptItem) => attemptItem.attempt
        );

        return {
          job: jobResult.job,
          attempts: attemptsValue,
          logsByAttempt: Object.fromEntries(
            jobResult.attempts.map((attemptItem) => [
              attemptItem.attempt.id,
              attemptItem.logs,
            ])
          ),
        };
      },
      schema: this,
    };
  }

  static cancelShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Job>> {
    return {
      ...super.partialUpdateShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<Job> => {
        const jobResult: {
          job: JobItem;
          attempts: { attempt: Attempt; logs: Logs }[];
        } = await this.fetch("post", `${this.url(params)}/cancel`, params);

        const attemptsValue = jobResult.attempts.map(
          (attemptItem) => attemptItem.attempt
        );

        return {
          job: jobResult.job,
          attempts: attemptsValue,
          logsByAttempt: Object.fromEntries(
            jobResult.attempts.map((attemptItem) => [
              attemptItem.attempt.id,
              attemptItem.logs,
            ])
          ),
        };
      },
      schema: this,
    };
  }
}
