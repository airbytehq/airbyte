#!/usr/bin/env node

/**
 * Custom Markdown Generator for OpenAPI Documentation
 *
 * This module provides a custom createApiPageMD function that can be used
 * with the docusaurus-plugin-openapi-docs markdownGenerators option.
 *
 * It automatically:
 * - Calls the default markdown generator to get complete markdown content
 * - Detects endpoints with SourceConfiguration or DestinationConfiguration
 * - Extracts request body parameters and builds api-endpoints-dereferenced.json
 * - Replaces RequestSchema with SourceRequestSchema and passes pageId
 */

const fs = require('fs');
const path = require('path');
const { createApiPageMD: defaultCreateApiPageMD } = require('docusaurus-plugin-openapi-docs/lib/markdown');

// In-memory cache for endpoints data (built incrementally as pages are generated)
let endpointsData = {};
let dataFilePath = null;

/**
 * Custom API page markdown generator
 *
 * @param {Object} pageData - The API page metadata from the openapi plugin
 * @param {Object} pageData.api - The operation object containing request/response details
 * @param {string} pageData.api.operationId - The operationId of the endpoint
 * @returns {string} The custom markdown with enhanced components
 */
function createApiPageMD(pageData) {
  // Get the default markdown by calling the default generator
  let markdown = defaultCreateApiPageMD(pageData);

  // Check if this endpoint has a SourceConfiguration or DestinationConfiguration
  const endpointInfo = extractEndpointInfo(pageData);

  if (endpointInfo && pageData.id) {
    // Use pageId as the key for the endpoint data
    const pageId = pageData.id;
    endpointsData[pageId] = endpointInfo;

    // Save to file (overwrites each time, but that's OK since we build incrementally)
    saveEndpointsData();

    // Replace RequestSchema based on where the configuration is found
    const { hasRequestConfiguration, hasResponseConfiguration } = endpointInfo;

    if (hasRequestConfiguration) {
      // Replace RequestSchema imports
      const importPattern =
        /import\s+RequestSchema\s+from\s+["']@theme\/RequestSchema["'];?/g;
      markdown = markdown.replace(
        importPattern,
        "// SourceRequestSchema is auto-registered in MDXComponents",
      );

      // Replace <RequestSchema ... /> components
      const componentPattern = /<RequestSchema\s+[^>]*\/>/gs;
      markdown = markdown.replace(
        componentPattern,
        `<SourceRequestSchema pageId="${pageId}" />`,
      );

      // Replace <RequestSchema ... > ... </RequestSchema> components
      const multilinePattern =
        /<RequestSchema\s+[^>]*>[\s\S]*?<\/RequestSchema>/g;
      markdown = markdown.replace(
        multilinePattern,
        `<SourceRequestSchema pageId="${pageId}" />`,
      );

      // Remove StatusCodes import
      const statusCodesImportPattern =
        /import\s+StatusCodes\s+from\s+["']@theme\/StatusCodes["'];?\n?/g;
      markdown = markdown.replace(statusCodesImportPattern, "");

      // Remove <StatusCodes ... /> components
      const statusCodesComponentPattern = /<StatusCodes\s+[^>]*\/>/gs;
      markdown = markdown.replace(statusCodesComponentPattern, "");

      // Remove <StatusCodes ... > ... </StatusCodes> components
      const statusCodesMultilinePattern =
        /<StatusCodes\s+[^>]*>[\s\S]*?<\/StatusCodes>/g;
      markdown = markdown.replace(statusCodesMultilinePattern, "");
    } else if (hasResponseConfiguration) {
      // For response-only endpoints, replace StatusCodes with TBD placeholder
      // Don't touch RequestSchema - it's part of the response schema

      // Replace StatusCodes import
      const statusCodesImportPattern =
        /import\s+StatusCodes\s+from\s+["']@theme\/StatusCodes["'];?\n?/g;
      markdown = markdown.replace(statusCodesImportPattern, "");

      // Replace <StatusCodes ... /> components with TBD
      const statusCodesComponentPattern = /<StatusCodes\s+[^>]*\/>/gs;
      markdown = markdown.replace(
        statusCodesComponentPattern,
        "TBD: Response Schema Component",
      );

      // Replace <StatusCodes ... > ... </StatusCodes> components with TBD
      const statusCodesMultilinePattern =
        /<StatusCodes\s+[^>]*>[\s\S]*?<\/StatusCodes>/g;
      markdown = markdown.replace(
        statusCodesMultilinePattern,
        "TBD: Response Schema Component",
      );
    }
  }

  return markdown;
}

/**
 * Extract endpoint information if it has SourceConfiguration or DestinationConfiguration
 * in either the request body or response
 */
function extractEndpointInfo(pageData) {
  if (!pageData.api) {
    return null;
  }

  try {
    // Get schemas from request body and response
    const requestBodySchema = pageData.api.requestBody?.content?.['application/json']?.schema;
    const successfulResponse = pageData.api.responses?.['200'] || pageData.api.responses?.['201'];
    const responseSchema = successfulResponse?.content?.['application/json']?.schema;

    // Check request body for configuration
    let requestInfo = null;
    if (requestBodySchema?.properties) {
      requestInfo = extractConfigurationInfo(requestBodySchema, 'request');
    }

    // Check response for configuration
    let responseInfo = null;
    if (responseSchema?.properties) {
      responseInfo = extractConfigurationInfo(responseSchema, 'response');
    }

    // If we found configuration in either request or response, return the data
    if (requestInfo) {
      return {
        operationId: pageData.api.operationId,
        path: pageData.api.servers?.[0]?.url || '/',
        method: pageData.api.method?.toUpperCase() || 'POST',
        requestBodyProperties: requestInfo.properties,
        configurationSchema: requestInfo.configProp,
        hasRequestConfiguration: true,
        hasResponseConfiguration: !!responseInfo
      };
    }

    // If only response has configuration, add a note for now
    if (responseInfo) {
      return {
        operationId: pageData.api.operationId,
        path: pageData.api.servers?.[0]?.url || '/',
        method: pageData.api.method?.toUpperCase() || 'POST',
        requestBodyProperties: [],
        configurationSchema: responseInfo.configProp,
        hasRequestConfiguration: false,
        hasResponseConfiguration: true,
        note: 'Response contains SourceConfiguration - custom component needed for rendering'
      };
    }

    return null;
  } catch (error) {
    // Silently ignore errors - not all endpoints have the structure we're looking for
    return null;
  }
}

/**
 * Extract configuration information from a schema
 * @param {Object} schema - The schema to check
 * @param {string} source - Either 'request' or 'response'
 * @returns {Object|null} Configuration info or null
 */
function extractConfigurationInfo(schema, source) {
  // Check if configuration property has SourceConfiguration or DestinationConfiguration title
  const configProp = schema.properties?.configuration || schema.properties?.destinationConfiguration;
  if (!configProp) {
    return null;
  }

  // Check if it's a SourceConfiguration or DestinationConfiguration
  const isSourceConfig = configProp.title === 'SourceConfiguration';
  const isDestConfig = configProp.title === 'DestinationConfiguration';

  if (!isSourceConfig && !isDestConfig) {
    return null;
  }

  // Extract properties
  const properties = [];
  const required = schema.required || [];

  for (const [name, prop] of Object.entries(schema.properties)) {
    properties.push({
      name,
      type: prop.type || 'string',
      required: required.includes(name),
      description: prop.description || ''
    });
  }

  return {
    configProp,
    properties
  };
}

/**
 * Save endpoints data to file
 */
function saveEndpointsData() {
  try {
    // Determine output path (same as component imports)
    if (!dataFilePath) {
      // Find the docusaurus root by looking for package.json
      let currentDir = __dirname;
      while (!fs.existsSync(path.join(currentDir, 'package.json'))) {
        const parentDir = path.dirname(currentDir);
        if (parentDir === currentDir) {
          // Reached filesystem root without finding package.json
          console.warn('Could not find docusaurus root directory');
          return;
        }
        currentDir = parentDir;
      }
      dataFilePath = path.join(currentDir, 'src/data/api-endpoints-dereferenced.json');
    }

    // Ensure directory exists
    const dir = path.dirname(dataFilePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write file
    fs.writeFileSync(dataFilePath, JSON.stringify(endpointsData, null, 2), 'utf-8');
  } catch (error) {
    console.warn('Failed to save endpoints data:', error.message);
  }
}

module.exports = {
  createApiPageMD
};
