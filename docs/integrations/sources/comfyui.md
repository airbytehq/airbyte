# ComfyUI Cloud

The ComfyUI Cloud source connector extracts generation jobs, assets, models, nodes, and system data from the [ComfyUI Cloud API](https://docs.comfy.org/api-reference/cloud) into any Airbyte destination.

[ComfyUI](https://www.comfy.org) is the open-source AI creation engine for visual professionals — a node-based interface for Stable Diffusion, Flux, and other generative AI models.

## Prerequisites

- A ComfyUI Cloud account
- An API key generated from [platform.comfy.org/profile/api-keys](https://platform.comfy.org/profile/api-keys)

## Supported streams

This source supports the following streams:

| Stream           | Sync Mode    | Description                                                             |
| :--------------- | :----------- | :---------------------------------------------------------------------- |
| **jobs**         | Incremental  | Generation job history with status, timing, and workflow references     |
| **job_details**  | Incremental  | Full job data including workflow graph, outputs, and execution metadata |
| **assets**       | Incremental  | User assets with tags, metadata, sizes, and preview URLs                |
| **models**       | Full Refresh | Available AI model catalog organized by folder                          |
| **nodes**        | Full Refresh | Node type catalog with inputs, outputs, and categories                  |
| **system_stats** | Full Refresh | System information including GPU, VRAM, and ComfyUI version             |

## Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | No         |

## Configuration

| Parameter    | Type   | Required | Default                   | Description                                   |
| :----------- | :----- | :------- | :------------------------ | :-------------------------------------------- |
| **API Key**  | string | Yes      | —                         | ComfyUI Cloud API key from platform.comfy.org |
| **Base URL** | string | No       | `https://cloud.comfy.org` | ComfyUI Cloud API base URL                    |

## Changelog

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.1.0   | 2026-05-18 | [78142](https://github.com/airbytehq/airbyte/pull/78142) | Initial release with 6 streams |
