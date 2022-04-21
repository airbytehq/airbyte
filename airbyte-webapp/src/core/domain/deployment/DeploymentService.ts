import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { exportArchive, importArchive } from "../../request/GeneratedApi";

export class DeploymentService extends AirbyteRequestService {
  public async exportDeployment() {
    const blob = await exportArchive(this.requestOptions);
    return window.URL.createObjectURL(blob);
  }

  public async importDeployment(file: Blob) {
    await importArchive(file, this.requestOptions);
  }
}
