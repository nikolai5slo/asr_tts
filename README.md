# openai_stt
# OpenAI STT Custom Component for Home Assistant

This custom component integrates OpenAI's Speech-To-Text (stt) service with Home Assistant, for people that run on Raspberry Pi and can't decently run Whisper locally.

This was made possible using the work of [sfortis's openai_tts](https://github.com/sfortis/openai_tts).

## Description

The OpenAI STT component for Home Assistant makes it possible to use the OpenAI API to generate text from spoken audio. This can be used in assistants. *You need an openAI API key.*

## Features

- Speech-To-Text conversion using OpenAI's API
- Support for multiple languages
- Integration with Home Assistant's assistant

## Installation Instructions

1. Ensure you have a `custom_components` folder within your Home Assistant configuration directory.

2. Inside the `custom_components` folder, create a new folder named `openai_stt`.

3. Place the repo files inside `openai_stt` folder.

4. Restart Home Assistant

5. Configure the component in your `configuration.yaml` file:

```yaml
stt:
  - platform: openai_stt
    api_key: "your_api_key_here"
    # Optional parameters:
    language: "en-US"
    model: "whisper-1"
