import { AirbyteRequestService } from "core/request/AirbyteRequestService";

export class DeploymentService extends AirbyteRequestService {
  static path = "deployment";

  getPath(subpath: string): string {
    return `${DeploymentService.path}/${subpath}`;
  }

  public async exportDeployment(): Promise<string> {
    const res = await this.fetch(this.getPath("export"), {});
    const blob = await res.blob();
    const objUrl = window.URL.createObjectURL(blob);

    return objUrl;
  }

  public async importDeployment(file: string | ArrayBuffer): Promise<void> {
    const options: RequestInit = {
      headers: {
        "Content-Type": "application/x-gzip",
        "Content-Encoding": "gzip",
      },
      body: file,
    };
    await this.fetch(this.getPath(`import`), undefined, options);

    return;
  }
}
