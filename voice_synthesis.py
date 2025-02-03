from elevenlabs import play
from elevenlabs.client import ElevenLabs

client = ElevenLabs()


def gen_dub(text):
    print("Generating audio...")
    audio = client.generate(
        text=text, model="eleven_flash_v2_5", stream=True, optimize_streaming_latency=1
    )
    play(audio)


if __name__ == "__main__":
    gen_dub("Hello world!")
