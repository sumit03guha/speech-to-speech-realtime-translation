import asyncio
from signal import SIGINT, SIGTERM

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
    Microphone,
)
from dotenv import load_dotenv

load_dotenv()

from llm import translate
from voice_synthesis import gen_dub

is_finals = []


async def stt_main(input_language: str, output_language: str) -> None:
    if input_language == "" or output_language == "":
        raise ValueError(
            "The input language and output language must be provided. Please provide the languages you want to translate from and to."
        )

    parsed_input_language: str = parse_input_language(input_language)
    try:
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        for signal in (SIGTERM, SIGINT):
            loop.add_signal_handler(
                signal,
                lambda: asyncio.create_task(
                    shutdown(signal, loop, dg_connection, microphone)
                ),
            )

        # logging values: WARNING, VERBOSE, DEBUG, SPAM
        config: DeepgramClientOptions = DeepgramClientOptions(
            options={"keepalive": "true"}
        )
        deepgram: DeepgramClient = DeepgramClient("", config)

        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_open(self, open, **kwargs):
            print("Connection Open. Waiting for speech...")

        async def on_message(self, result, **kwargs) -> None:
            global is_finals
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                # We need to collect these and concatenate them together when we get a speech_final=true
                # See docs: https://developers.deepgram.com/docs/understand-endpointing-interim-results
                is_finals.append(sentence)

                # Speech Final means we have detected sufficient silence to consider this end of speech
                # Speech final is the lowest latency result as it triggers as soon an the endpointing value has triggered
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    print(f"Speech Final: {utterance}")
                    translation = translate(str(utterance), output_language)
                    print(f"Translation: {translation}")
                    gen_dub(translation)
                    is_finals = []
                else:
                    # These are useful if you need real time captioning and update what the Interim Results produced
                    print(f"Is Final: {sentence}")
            else:
                # These are useful if you need real time captioning of what is being spoken
                print(f"Interim Results: {sentence}")

        async def on_metadata(self, metadata, **kwargs):
            print(f"Metadata: {metadata}")

        async def on_speech_started(self, speech_started, **kwargs):
            print("Speech Started")

        async def on_utterance_end(self, utterance_end, **kwargs):
            print("Utterance End")
            global is_finals
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                print(f"Utterance End: {utterance}")
                is_finals = []

        async def on_close(self, close, **kwargs):
            print("Connection Closed")

        async def on_error(self, error, **kwargs):
            print(f"Handled Error: {error}")

        async def on_unhandled(self, unhandled, **kwargs):
            print(f"Unhandled Websocket Message: {unhandled}")

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

        # connect to websocket
        options: LiveOptions = LiveOptions(
            model="nova-2",
            language=parsed_input_language,
            # Apply smart formatting to the output
            smart_format=True,
            # Raw audio format deatils
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            # To get UtteranceEnd, the following must be set:
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            # Time in milliseconds of silence to wait for before finalizing speech
            endpointing=300,
        )

        addons: dict[str, str] = {
            # Prevent waiting for additional numbers
            "no_delay": "true"
        }

        print("\n\nStart talking! Press Ctrl+C to stop...\n")
        if await dg_connection.start(options, addons=addons) is False:
            print("Failed to connect to Deepgram")
            return

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()

        # wait until cancelled
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # This block will be executed when the shutdown coroutine cancels all tasks
            pass
        finally:
            microphone.finish()
            await dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return


async def shutdown(signal, loop, dg_connection, microphone):
    print(f"Received exit signal {signal.name}...")
    microphone.finish()
    await dg_connection.finish()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    print("Shutdown complete.")


def parse_input_language(input_language: str) -> str:
    """
    Parse the input language to Deepgram's supported language format.
    Supported languages and their code - https://developers.deepgram.com/docs/models-languages-overview
    """

    language_map: dict[str, str] = {
        "bulgarian": "bg",
        "catalan": "ca",
        "chinese": "zh",
        "czech": "cs",
        "danish": "da",
        "dutch": "nl",
        "english": "en",
        "estonian": "et",
        "finnish": "fi",
        "flemish": "nl",
        "french": "fr",
        "german": "de",
        "greek": "el",
        "hindi": "hi",
        "hungarian": "hu",
        "indonesian": "id",
        "italian": "it",
        "japanese": "ja",
        "korean": "ko",
        "latvian": "lv",
        "lithuanian": "lt",
        "malay": "ms",
        "norwegian": "no",
        "polish": "pl",
        "portuguese": "pt",
        "romanian": "ro",
        "russian": "ru",
        "slovak": "sk",
        "spanish": "es",
        "swedish": "sv",
        "thai": "th",
        "turkish": "tr",
        "ukrainian": "uk",
        "vietnamese": "vi",
    }

    input_language_lower: str = input_language.lower()

    if input_language_lower in language_map:
        return language_map[input_language_lower]
    else:
        raise ValueError(
            "The input language is not supported. Please choose a language supported by Deepgram."
        )
