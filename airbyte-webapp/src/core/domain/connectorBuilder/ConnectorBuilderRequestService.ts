import {
  getManifestTemplate,
  listStreams,
  readStream,
  StreamRead,
  StreamReadRequestBody,
  StreamsListRead,
  StreamsListRequestBody,
} from "core/request/ConnectorBuilderClient";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";
export class ConnectorBuilderRequestService extends AirbyteRequestService {
  public readStream(readParams: StreamReadRequestBody): Promise<StreamRead> {
    return readStream(readParams, { ...this.requestOptions, config: { apiUrl: "http://localhost:8080" } });
  }

  public listStreams(listParams: StreamsListRequestBody): Promise<StreamsListRead> {
    return listStreams(listParams, { ...this.requestOptions, config: { apiUrl: "http://localhost:8080" } });
  }

  public getManifestTemplate(): Promise<string> {
    return getManifestTemplate({ ...this.requestOptions, config: { apiUrl: "http://localhost:8080" } });
  }
}
