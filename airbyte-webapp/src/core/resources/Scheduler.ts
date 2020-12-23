import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";
import { propertiesType } from "./SourceDefinitionSpecification";
import { Attempt, JobItem } from "./Job";

type JobInfo = {
  job: JobItem;
  attempts: {
    attempt: Attempt;
    logs: { logLines: string[] };
  }[];
};

export interface Scheduler {
  status: string;
  message: string;
  job_info?: JobInfo;
}

export default class SchedulerResource extends BaseResource
  implements Scheduler {
  readonly status: string = "";
  readonly message: string = "";
  readonly job_info: JobInfo | undefined = undefined;

  pk() {
    return Date.now().toString();
  }

  static urlRoot = "scheduler";

  static sourceCheckConnectionShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        sourceDefinitionId: string;
        connectionConfiguration: propertiesType;
      }) => `POST /scheduler/sources/check_connection` + JSON.stringify(params),
      fetch: async (params: any): Promise<any> => {
        return await this.fetch(
          "post",
          `${this.url(params)}/sources/check_connection`,
          params
        );
      },
      schema: this.asSchema()
    };
  }
}
