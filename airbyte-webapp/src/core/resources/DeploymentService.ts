import AirbyteRequestService from "./AirbyteRequestService";

export default class DeploymentService extends AirbyteRequestService {
  static path = "deployment";

  static getPath(subpath: string): string {
    return `${this.rootUrl}${this.path}/${subpath}`;
  }

  static async exportDeployment(): Promise<string> {
    const res = await this.fetch(this.getPath("export"), {});
    const blob = await res.blob();
    const objUrl = window.URL.createObjectURL(blob);

    return objUrl;
  }

  static async importDeployment(file: string | ArrayBuffer): Promise<void> {
    const options: RequestInit = {
      headers: {
        "Content-Type": "application/x-gzip",
        "Content-Encoding": "gzip",
      },
      body: file,
    };
    console.log(file);
    const result = await this.fetch(this.getPath(`import`), options);

    console.log(result);
    console.log(result);

    return;
  }
}
