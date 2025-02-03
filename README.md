# Speech-to-Speech Realtime Translation Without OpenAI Realtime

This project provides a real-time speech-to-speech translation system using Deepgram for speech recognition, LangChain for language translation, and ElevenLabs for voice synthesis.

## Features

- Real-time speech recognition using Deepgram
- Language translation using LangChain and OpenAI's GPT model **(not using OpenAI's real-time model, so it won't be pricey)**
- Voice synthesis using ElevenLabs

## Requirements

- Python 3.12.0
- Deepgram API key
- OpenAI API key
- ElevenLabs API key

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/speech-to-speech-realtime-translation.git
    cd speech-to-speech-realtime-translation
    ```

2. Install dependencies using Poetry or pip:

    ```sh
    poetry install
    ```

    or

    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file based on the [.env.example](./.env.example) file and add your API keys:

    ```sh
    cp .env.example .env
    ```

    Fill in the `.env` file with your API keys:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    DEEPGRAM_API_KEY=your_deepgram_api_key
    ELEVEN_API_KEY=your_elevenlabs_api_key
    ```

## Usage

1. Run the main script:

    ```sh
    poetry run python main.py
    ```

2. Follow the prompts to enter the input and output languages.

## Project Structure

- [main.py](./main.py): Entry point of the application.
- [stt_streaming.py](./stt_streaming.py): Handles real-time speech recognition and translation.
- [llm.py](./llm.py): Contains the logic for language translation using LangChain and OpenAI.
- [voice_synthesis.py](./voice_synthesis.py): Handles voice synthesis using ElevenLabs.
- [requirements.txt](./pyproject.toml): Lists the required Python packages.
- [pyproject.toml](./pyproject.toml): Configuration file for Poetry.
- [.env.example](./.env.example): Example environment variables file.

## License

This project is licensed under the MIT License.
