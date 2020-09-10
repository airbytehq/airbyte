import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Job {
  id: string;
  config_type: string;
  config_id: string;
  created_at: number;
  started_at: number;
  updated_at: number;
  status: string;
}

export default class JobResource extends BaseResource implements Job {
  readonly id: string = "";
  readonly config_type: string = "";
  readonly config_id: string = "";
  readonly created_at: number = 0;
  readonly started_at: number = 0;
  readonly updated_at: number = 0;
  readonly status: string = "";

  pk() {
    return this.id?.toString();
  }

  static urlRoot = "jobs";

  // static listShape<T extends typeof Resource>(this: T) {
  //   return {
  //     ...super.listShape(),
  //     schema: { jobs: [this.asSchema()] }
  //   };
  // }

  // TODO: delete this test data
  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { jobs: [this.asSchema()] },
      fetch: async (): Promise<any> => {
        return {
          jobs: [
            {
              id: "1",
              config_type: "check_connection_source",
              config_id: "test_id_1",
              created_at: 1459832991883,
              started_at: 0,
              updated_at: 0,
              status: "pending"
            },
            {
              id: "2",
              config_type: "check_connection_source",
              config_id: "test_id_2",
              created_at: 1459832991883,
              started_at: 0,
              updated_at: 0,
              status: "fail"
            },
            {
              id: "3",
              config_type: "check_connection_source",
              config_id: "test_id_3",
              created_at: 1459832991883,
              started_at: 0,
              updated_at: 0,
              status: "success"
            }
          ]
        };
      }
    };
  }
}
