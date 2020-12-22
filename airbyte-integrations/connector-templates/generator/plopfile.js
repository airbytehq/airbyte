'use strict';
const fs = require('fs');
const path = require('path');

const getSuccessMessage = function(connectorName, outputPath){
    return `
🚀 🚀 🚀 🚀 🚀 🚀

Success! 

Your ${connectorName} connector has been created at ${path.resolve(outputPath)}.

Follow instructions in NEW_SOURCE_CHECKLIST.md to finish your connector.

Questions, comments, or concerns? Let us know at:
Slack: https://slack.airbyte.io
Github: https://github.com/airbytehq/airbyte

We're always happy to provide you with any support :)
`
}

module.exports = function (plop) {
  const pythonSourceInputRoot = '../source-python';
  const singerSourceInputRoot = '../source-singer';
  const genericSourceInputRoot = '../source-generic';

  const basesDir = '../../bases';
  const outputDir = '../../connectors';
  const pythonSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;
  const singerSourceOutputRoot = `${outputDir}/source-{{dashCase name}}-singer`;
  const genericSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;

  plop.setActionType('emitSuccess', function(answers, config, plopApi){
      console.log(getSuccessMessage(answers.name, plopApi.renderString(config.outputPath, answers)));
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
      {type: 'emitSuccess', outputPath: pythonSourceOutputRoot}]
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
        {type: 'emitSuccess', outputPath: singerSourceOutputRoot},
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
          {type: 'emitSuccess', outputPath: genericSourceOutputRoot}
      ]
    });


};
