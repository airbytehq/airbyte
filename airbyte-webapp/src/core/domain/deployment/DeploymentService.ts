import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { AirbyteArchive, exportArchive, importArchive } from "../../request/GeneratedApi";

export class DeploymentService extends AirbyteRequestService {
  public async exportDeployment() {
    const blob = await exportArchive(this.requestOptions);
    return window.URL.createObjectURL(blob);
  }

  public async importDeployment(file: AirbyteArchive) {
    await importArchive(file, this.requestOptions);
  }
}
