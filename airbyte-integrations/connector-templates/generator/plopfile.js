'use strict';
const fs = require('fs');
const path = require('path');

module.exports = function (plop) {
  const javaDestinationInputRoot = '../java-destination';
  const pythonSourceInputRoot = '../source-python';
  const singerSourceInputRoot = '../source-singer';
  const genericSourceInputRoot = '../source-generic';

  const basesDir = '../../bases';
  const outputDir = '../../connectors';
  const javaDestinationOutputRoot = `${outputDir}/destination-{{dashCase name}}`;
  const pythonSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;
  const singerSourceOutputRoot = `${outputDir}/source-{{dashCase name}}-singer`;
  const genericSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;

  plop.setGenerator('Java Destination', {
    description: 'Generate an Airbyte destination written in Java',
    prompts: [
      {
        type: 'input',
        name: 'name',
        message: 'destination name (without the "destination" suffix; e.g. "my sql")'
      }
    ],
    actions: [
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/build.gradle`,
        templateFile: `${javaDestinationInputRoot}/build.gradle.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/src/main/java/io/airbyte/integrations/destination/{{snakeCase name}}/{{properCase name}}Destination.java`,
        templateFile: `${javaDestinationInputRoot}/Destination.java.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/Dockerfile`,
        templateFile: `${javaDestinationInputRoot}/Dockerfile.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/.dockerignore`,
        templateFile: `${javaDestinationInputRoot}/.dockerignore.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/spec.json`,
        templateFile: `${javaDestinationInputRoot}/spec.json.hbs`,
      },
      'Your new connector has been created. Happy coding~~',
    ],
  });

  plop.setGenerator('Python Source', {
    description: 'Generate an Airbyte Source written in Python',
    prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
    actions: [
        {
        abortOnFail: true,
        type:'addMany',
        destination: pythonSourceOutputRoot,
        base: pythonSourceInputRoot,
        templateFiles: `${pythonSourceInputRoot}/**/**`,
        globOptions: {ignore:'.secrets'}
      },
        // plop doesn't add dotfiles by default so we manually add them
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${pythonSourceInputRoot}/.secrets/config.json.hbs`,
        path: `${pythonSourceOutputRoot}/secrets/config.json`
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${pythonSourceInputRoot}/.gitignore.hbs`,
        path: `${pythonSourceOutputRoot}/.gitignore`
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${pythonSourceInputRoot}/.dockerignore.hbs`,
        path: `${pythonSourceOutputRoot}/.dockerignore`
      },
      function(answers, config, plop){
        const renderedOutputDir = plop.renderString(pythonSourceOutputRoot, answers);
        fs.symlinkSync(`${basesDir}/base-python/base_python`, `${renderedOutputDir}/base_python`);
        fs.symlinkSync(`${basesDir}/airbyte-protocol/airbyte_protocol`, `${renderedOutputDir}/airbyte_protocol`);
      },
      'Your new Python source connector has been created. Follow the instructions and TODOs in the newly created package for next steps. Happy coding! 🐍🐍',]
  });

  plop.setGenerator('Singer-based Python Source', {
    description: 'Generate an Airbyte Source written on top of a Singer Tap.',
    prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
    actions: [
      {
        abortOnFail: true,
        type:'addMany',
        destination: singerSourceOutputRoot,
        base: singerSourceInputRoot,
        templateFiles: `${singerSourceInputRoot}/**/**`,
        globOptions: {ignore:'.secrets'}
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${singerSourceInputRoot}/.secrets/config.json.hbs`,
        path: `${singerSourceOutputRoot}/secrets/config.json`
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${singerSourceInputRoot}/.gitignore.hbs`,
        path: `${singerSourceOutputRoot}/.gitignore`
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${singerSourceInputRoot}/.dockerignore.hbs`,
        path: `${singerSourceOutputRoot}/.dockerignore`
      },
      function(answers, config, plop){
        const renderedOutputDir = plop.renderString(singerSourceOutputRoot, answers);
        fs.symlinkSync(`${basesDir}/base-python/base_python`, `${renderedOutputDir}/base_python`);
        fs.symlinkSync(`${basesDir}/airbyte-protocol/airbyte_protocol`, `${renderedOutputDir}/airbyte_protocol`);
        fs.symlinkSync(`${basesDir}/base-singer/base_singer`, `${renderedOutputDir}/base_singer`);
      },
      'Your new Singer-based source connector has been created. Follow the instructions and TODOs in the newly created package for next steps. Happy coding! 🐍🐍',
    ]
  });

  plop.setGenerator('Generic Source', {
      description: 'Use if none of the other templates apply to your use case.',
      prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
      actions: [
        {
          abortOnFail: true,
          type:'addMany',
          destination: genericSourceOutputRoot,
          base: genericSourceInputRoot,
          templateFiles: `${genericSourceInputRoot}/**/**`,
          globOptions: {ignore:'.secrets'}
        },
        {
          type:'add',
          abortOnFail: true,
          templateFile: `${genericSourceInputRoot}/.gitignore.hbs`,
          path: `${genericSourceOutputRoot}/.gitignore`
        },
        'Your new connector package has been created. Follow the instructions and TODOs in the newly created package for next steps. Happy coding! 🚀',
      ]
    });
};
