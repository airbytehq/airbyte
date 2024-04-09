import React, {useState} from 'react';
import CodeBlock from '@theme/CodeBlock';

function simpleProperty(name, type) {
  return [name, { type }];
}

function dateProperty(name, format, airbyteType) {
  const definition = {
    type: ['null', 'string'],
    format,
  };
  if (airbyteType !== null) {
    definition.airbyte_type = airbyteType;
  }
  return [name, definition];
}

const allSupportedColumnTypePropertyGenerators = [
  (i) => simpleProperty(`string_${i}`, 'string'),
  (i) => simpleProperty(`boolean_${i}`, 'boolean'),
  (i) => dateProperty(`date_${i}`, 'date', null),
  (i) => dateProperty(`timestamp_wo_tz_${i}`, 'date-time', 'timestamp_without_timezone'),
  (i) => dateProperty(`timestamp_w_tz_${i}`, 'date-time', 'timestamp_with_timezone'),
  (i) => dateProperty(`time_wo_tz_${i}`, 'time', 'time_without_timezone'),
  (i) => dateProperty(`time_w_tz_${i}`, 'time', 'time_with_timezone'),
  (i) => simpleProperty(`integer_${i}`, 'integer'),
  (i) => simpleProperty(`number_${i}`, 'number'),
  (i) => simpleProperty(`array_${i}`, 'array'),
  (i) => simpleProperty(`object_${i}`, 'object'),
];

function generateWideSchema(columns) {

  const fullSchema = { type: 'object' };
  const properties = {};

  // Special case id and updated_at column
  const id = simpleProperty('id', 'integer');
  properties[id[0]] = id[1];
  properties['updated_at'] = { type: 'string', format: 'date-time', airbyte_type: 'timestamp_with_timezone' };

  let columnCount = 2;
  let propertyGeneratorIndex = 0;

  while (columnCount < columns) {
    const propertyInfo = allSupportedColumnTypePropertyGenerators[propertyGeneratorIndex](columnCount);
    properties[propertyInfo[0]] = propertyInfo[1];

    propertyGeneratorIndex += 1;
    if (propertyGeneratorIndex === allSupportedColumnTypePropertyGenerators.length) {
      propertyGeneratorIndex = 0;
    }

    columnCount += 1;
  }

  fullSchema.properties = properties;

  return fullSchema;
}




export const SchemaGenerator = () => {

  const [generatedSchema, updateGeneratedSchema] = useState({
    'schema' : JSON.stringify(generateWideSchema(10))
  })
  function updateSchema(event) {
    const columns = parseInt(document.getElementById("schema-generator-column-count").value)
    const schema = JSON.stringify(generateWideSchema(columns))
    updateGeneratedSchema({'schema': schema})
  }

  return (
      <div>
        <label for="schema-generator-column-count">Desired Number of Columns:</label>
        <input type="number" id="schema-generator-column-count" name="schema-generator-column-count" onChange={updateSchema}/>
        <p>Generated Schema:</p>
        <CodeBlock id={"generated_e2e_test_schema"} language={"javascript"}>
          { generatedSchema['schema'] }
        </CodeBlock>
      </div>
  )
}
