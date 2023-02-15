import {
  getManifestTemplate,
  listStreams,
  readStream,
  resolveManifest,
  ResolveManifestRequestBody,
  StreamRead,
  StreamReadRequestBody,
  StreamsListRead,
  StreamsListRequestBody,
} from "core/request/ConnectorBuilderClient";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";
export class ConnectorBuilderRequestService extends AirbyteRequestService {
  public readStream(readParams: StreamReadRequestBody): Promise<StreamRead> {
    return readStream(readParams, this.requestOptions);
  }

  public listStreams(listParams: StreamsListRequestBody): Promise<StreamsListRead> {
    return listStreams(listParams, this.requestOptions);
  }

  public getManifestTemplate(): Promise<string> {
    return getManifestTemplate(this.requestOptions);
  }

  public resolveManifest(resolveParams: ResolveManifestRequestBody) {
    return resolveManifest(resolveParams, this.requestOptions);
  }
}
