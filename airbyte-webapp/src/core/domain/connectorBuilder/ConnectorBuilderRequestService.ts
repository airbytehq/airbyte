import {
  StreamRead,
  StreamReadRequestBody,
  StreamsListRead,
  StreamsListRequestBody,
} from "core/request/ConnectorBuilderClient";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class ConnectorBuilderRequestService extends AirbyteRequestService {
  public readStream(readParams: StreamReadRequestBody): Promise<StreamRead> {
    // TODO: uncomment this and remove mock responses once there is a real API to call
    // return readStream(readParams, this.requestOptions);
    console.log("------------");
    console.log(`Stream: ${readParams.stream}`);
    console.log(`Connector manifest:\n${JSON.stringify(readParams.manifest)}`);
    console.log(`Config:\n${JSON.stringify(readParams.config)}`);
    return new Promise((resolve) => setTimeout(resolve, 200)).then(() => {
      return {
        logs: [
          { level: "INFO", message: `Syncing stream: ${readParams.stream}` },
          { level: "INFO", message: `Setting state of ${readParams.stream} to {'date': '2022-09-25'}` },
        ],
        slices: [
          {
            sliceDescriptor: { start: "Jan 1, 2022", end: "Jan 2, 2022" },
            state: {
              type: "STREAM",
              stream: { stream_descriptor: { name: readParams.stream }, stream_state: { date: "2022-09-26" } },
              data: { [readParams.stream]: { date: "2022-09-26" } },
            },
            pages: [
              {
                records: [
                  {
                    stream: readParams.stream,
                    data: {
                      id: "dp_123",
                      object: readParams.stream,
                      amount: 2000,
                      balance_transaction: "txn_123",
                    },
                  },
                ],
                request: {
                  url: `https://api.com/${readParams.stream}`,
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

  public listStreams(listParams: StreamsListRequestBody): Promise<StreamsListRead> {
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
