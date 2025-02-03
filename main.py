import asyncio

from dotenv import load_dotenv

load_dotenv()

from stt_streaming import stt_main

is_finals = []

if __name__ == "__main__":
    try:
        print(
            """
            The supported languages can be found here https://developers.deepgram.com/docs/models-languages-overview

            For example, if you want to translate from English, you can enter english,
            or, if you want to translate from Spanish, you can enter spanish.
            """
        )
        input_language: str = input(
            "Please enter the language you want to translate from: "
        )
        translated_language: str = input(
            "Please enter the language you want to translate to: "
        )

        asyncio.run(stt_main(input_language, translated_language))
    except Exception as e:
        print(f"An error occurred: {e}")
