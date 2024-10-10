# AI Inference Framework

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Client SDK Usage](#client-sdk-usage)
- [Services Deployment](#services-deployment)
  - [WHIP and WHEP Services](#whip-and-whep-services)
  - [RTMP Ingest Service](#rtmp-ingest-service)
  - [Pipeline Service](#pipeline-service)
- [Examples](#examples)
  - [1. Stable Diffusion XL (SDXL)](#1-stable-diffusion-xl-sdxl)
  - [2. Video Processing Pipeline](#2-video-processing-pipeline)
  - [3. LoRA](#3-lora)
- [Design Overview](#design-overview)
  - [Core Engine](#core-engine)
  - [Pipeline System](#pipeline-system)
  - [Plugin System](#plugin-system)
  - [Client SDK](#client-sdk)
- [Development](#development)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

The AI Inference Framework is a modular and extensible platform for processing video and image data using AI models. It allows users to define custom pipelines, integrate various models, and extend functionality through plugins. The framework supports real-time processing and can be used for applications like style transfer, image generation, and animation.

---

## Features

- **Modular Architecture**: Clean separation of concerns with core engine, pipeline, and plugins.
- **Custom Pipelines**: Define pipelines using YAML configurations.
- **Plugin System**: Extend functionality with custom functions and models.
- **Client SDK**: Interact with the framework using an easy-to-use Python SDK.
- **Independent Services**: WHIP, WHEP, RTMP ingest, and Pipeline services can be deployed independently.
- **Examples Included**: Ready-to-use examples with SDXL, video processing, and LoRA.

---

## Project Structure

ai_inference_framework/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── pipeline.py
│   │   ├── steps/
│   │   │   ├── __init__.py
│   │   │   ├── base_step.py
│   │   │   ├── function_step.py
│   │   │   └── model_step.py
│   │   └── utils.py
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── custom_functions.py
│   │   └── custom_models.py
│   └── services/
│       ├── __init__.py
│       ├── whip_ingest_server.py
│       ├── whep_playback_server.py
│       ├── rtmp_ingest_server.py
│       └── pipeline_service.py
├── configs/
│   ├── default_pipeline.yaml
│   ├── sdxl_pipeline.yaml
│   ├── video_pipeline.yaml
│   └── lora_pipeline.yaml
├── sdk/
│   ├── __init__.py
│   └── pipeline_client.py
├── tests/
│   ├── __init__.py
│   ├── test_pipeline.py
│   └── test_client.py
└── deployment/
    ├── __init__.py
    └── deploy.py
