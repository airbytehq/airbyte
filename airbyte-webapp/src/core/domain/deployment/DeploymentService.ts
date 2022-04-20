import { exportArchive, importArchive } from "../../request/GeneratedApi";

export class DeploymentService {
  public async exportDeployment(): Promise<string> {
    const blob = await exportArchive();
    return window.URL.createObjectURL(blob);
  }

  public async importDeployment(file: Blob) {
    await importArchive(file);
  }
}
