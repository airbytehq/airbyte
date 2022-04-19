import { AirbyteRequestService } from "core/request/AirbyteRequestService";

type ListParams = {
  configId: string;
  configTypes: string[];
};

class JobsService extends AirbyteRequestService {
  get url(): string {
    return "jobs";
  }

  public async list(listParams: ListParams): Promise<any> {
    const jobs = await this.fetch<any>(`${this.url}/list`, listParams);

    return jobs;
  }

  public async get(jobId: string | number): Promise<any> {
    const job = await this.fetch<any>(`${this.url}/get`, {
      id: jobId,
    });

    return job;
  }

  public async cancel(jobId: string | number): Promise<any> {
    const job = await this.fetch<any>(`${this.url}/cancel`, {
      id: jobId,
    });

    return job;
  }
}

export { JobsService };
export type { ListParams };
