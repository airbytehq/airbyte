import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { listProducts } from "../../request/DaspireClient";

const abc = "";
export class ProductService extends AirbyteRequestService {
  public list() {
    return listProducts(this.requestOptions);
  }
}
