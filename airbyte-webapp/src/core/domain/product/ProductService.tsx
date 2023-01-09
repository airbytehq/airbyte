import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { listProducts, packagesInfo } from "../../request/DaspireClient";

export class ProductService extends AirbyteRequestService {
  public list() {
    return listProducts(this.requestOptions);
  }

  public packagesDetail() {
    return packagesInfo(this.requestOptions);
  }
}
