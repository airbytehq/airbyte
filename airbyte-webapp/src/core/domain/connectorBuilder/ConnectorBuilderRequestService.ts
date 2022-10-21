import { StreamReadRequestBody, StreamsListRequestBody } from "core/request/ConnectorBuilderClient";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class ConnectorBuilderRequestService extends AirbyteRequestService {
  public readStream(readParams: StreamReadRequestBody) {
    // TODO: uncomment this and remove mock responses once there is a real API to call
    // return readStream(readParams, this.requestOptions);
    console.log("------------");
    console.log(`Stream: ${readParams.stream}`);
    console.log(`Connector manifest:\n${JSON.stringify(readParams.manifest)}`);
    console.log(`Config:\n${JSON.stringify(readParams.config)}`);
    return new Promise((resolve) => setTimeout(resolve, 200)).then(() => {
      return {
        slices: [
          {
            sliceDescriptor: { start: "Jan 1, 2022", end: "Jan 2, 2022" },
            pages: [
              {
                airbyteMessages: [
                  {
                    type: "RECORD",
                    record: {
                      stream: readParams.stream,
                      data: {
                        id: "dp_123",
                        object: readParams.stream,
                        amount: 2000,
                        balance_transaction: "txn_123",
                      },
                    },
                  },
                  {
                    type: "STATE",
                    state: {
                      data: {
                        timestamp: "2022-10-20T02:00:59Z",
                      },
                    },
                  },
                ],
                request: {
                  url: "https://api.com/path",
                },
                response: {
                  status: 200,
                },
              },
              {
                airbyteMessages: [
                  {
                    type: "RECORD",
                    record: {
                      stream: readParams.stream,
                      data: {
                        id: "dp_123",
                        object: readParams.stream,
                        amount: 2000,
                        balance_transaction: "txn_123",
                      },
                    },
                  },
                  {
                    type: "STATE",
                    state: {
                      data: {
                        timestamp: "2022-10-20T02:00:59Z",
                      },
                    },
                  },
                ],
                request: {
                  url: "https://api.com/path",
                },
                response: {
                  status: 200,
                },
              },
            ],
          },
        ],
      };
    });
  }

  public listStreams(listParams: StreamsListRequestBody) {
    // TODO: uncomment this and remove mock responses once there is a real API to call
    // return listStreams(listParams, this.requestOptions);
    console.log(`Received listStreams body: ${JSON.stringify(listParams)}`);
    return new Promise((resolve) => setTimeout(resolve, 200)).then(() => {
      return {
        streams: [
          {
            name: "disputes",
            url: "https://api.com/disputes",
          },
          {
            name: "transactions",
            url: "https://api.com/transactions",
          },
          {
            name: "users",
            url: "https://api.com/users",
          },
        ],
      };
    });
  }
}
