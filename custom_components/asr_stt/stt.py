import asyncio
import struct
import io
import logging
from collections.abc import AsyncIterable
import requests
import async_timeout
from requests_toolbelt.multipart.encoder import MultipartEncoder
from io import BytesIO
from pydub import AudioSegment, effects, silence
from time import time 

from homeassistant.components import stt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([ASRSTT(hass, config_entry)])


class ASRSTT(stt.SpeechToTextEntity):
    _attr_name = "ASR STT"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.api_url: str = config_entry.data["api_url"]
        self.language: str = config_entry.data["language"]

    @property
    def supported_languages(self) -> list[str]:
        return [self.language]

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> stt.SpeechResult:
        # Collect data
        audio_data = b""
        async for chunk in stream:
            audio_data += chunk

        url = self.api_url
        
        # Setup audio segment
        sound = AudioSegment(
            # raw audio data (bytes)
            data=audio_data,

            # 2 byte (16 bit) samples
            sample_width=2,

            # 16 kHz frame rate
            frame_rate=16000,

            # stereo
            channels=1
        )

        memory_file = io.BytesIO()

        # Export audio file to memory
        # end = silence.detect_leading_silence(sound.reverse())
        # sound = sound[silence.detect_leading_silence(sound):-end]
        sound = effects.normalize(sound) 
        sound.export(memory_file, format="wav")

        # memory_file = write_header(audio_data, 1, 2, 16000)
         
        files={'audio_file': ("audio%d.wav"%(int(time()),), memory_file, 'audio/wav')}

        def job():
            response = requests.post(url, files=files)
            if response.status_code == 200:
                _LOGGER.debug("Response: %s", response.text)
                return response.json()["result"]
            else:
                _LOGGER.error("%s", response.text)
                return ''

        async with async_timeout.timeout(10):
            assert self.hass
            response = await self.hass.async_add_executor_job(job)
            if len(response) > 0:
                return stt.SpeechResult(
                    response,
                    stt.SpeechResultState.SUCCESS,
                )
            return stt.SpeechResult("", stt.SpeechResultState.ERROR)


def write_header(_bytes, _nchannels, _sampwidth, _framerate):
    WAVE_FORMAT_PCM = 0x0001
    initlength = len(_bytes)
    bytes_to_add = b'RIFF'

    _nframes = initlength // (_nchannels * _sampwidth)
    _datalength = _nframes * _nchannels * _sampwidth

    bytes_to_add += struct.pack('<L4s4sLHHLLHH4s',
        36 + _datalength, b'WAVE', b'fmt ', 16,
        WAVE_FORMAT_PCM, _nchannels, _framerate,
        _nchannels * _framerate * _sampwidth,
        _nchannels * _sampwidth,
        _sampwidth * 8, b'data')

    bytes_to_add += struct.pack('<L', _datalength)

    return bytes_to_add + _bytes
