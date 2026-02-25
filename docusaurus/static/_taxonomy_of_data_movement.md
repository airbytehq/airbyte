People think about different types of data movement with a lot of nuance. At a high level, Airbyte thinks about them like the table below. Airbyte's data replication platform targets the first row in the table. Airbyte's agentic data platform targets the second row.

While the agentic data platform exists to support AI use cases, it's incorrect to say data replication doesn't support AI. For example, data replication is a core ingredient in Retrieval-Augmented Generation (RAG). Think about your approach to data movement in terms of getting your data into the right shape at the right time. Don't think about the choice as binary. It's safe to assume AI is a stakeholder of some kind in virtually every data movement operation.

<table>
  <tr>
    <th></th>
    <th>In</th>
    <th>Out (data activation)</th>
  </tr>
  <tr>
    <th>Data replication</th>
    <td>
      <strong>ELT/ETL</strong><br /><br />
      For when:
      <ul>
        <li>You need all the data</li>
        <li>You need to join across datasets</li>
        <li>You need more pipeline steps that are slow</li>
      </ul>
      Requires:
      <ul>
        <li>Storage</li>
      </ul>
    </td>
    <td>
      <strong>Reverse ETL</strong><br /><br />
      For when:
      <ul>
        <li>You have a lot of data to update</li>
        <li>You want to update content, not trigger side effects</li>
      </ul>
      Requires:
      <ul>
        <li>Good vendor APIs</li>
      </ul>
    </td>
  </tr>
  <tr>
    <th>Operations</th>
    <td>
      <strong>Get</strong><br /><br />
      For when:
      <ul>
        <li>You don't need all the data</li>
        <li>You don't want storage</li>
        <li>Freshness (latency) matters</li>
      </ul>
      Requires:
      <ul>
        <li>Good vendor APIs</li>
      </ul>
    </td>
    <td>
      <strong>Write</strong><br /><br />
      For when:
      <ul>
        <li>You're updating a small amount of data</li>
        <li>You want to trigger side effects, like sending an email or closing a ticket</li>
      </ul>
      Requires:
      <ul>
        <li>Good vendor APIs</li>
      </ul>
    </td>
  </tr>
</table>
