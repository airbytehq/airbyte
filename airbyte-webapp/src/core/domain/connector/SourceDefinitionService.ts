import { AirbyteRequestService } from '@app/core/request/AirbyteRequestService'
import { SourceDefinition } from '@app/core/resources/SourceDefinition'

class SourceDefinitionService extends AirbyteRequestService {
  get url() {
    return 'source_definitions'
  }

  public update(body: SourceDefinition): Promise<SourceDefinition> {
    return this.fetch(`${this.url}/update`, body) as any
  }
}

export { SourceDefinitionService }
