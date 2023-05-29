import threading
import json
import logging

from python_utils_aisu import utils, utils_japanese

from .text_handler import text_handler_japanese
from . import translate_google_utils
from . import tts_voicevox_utils

class TextHandlerJapaneseTtsVoicevox(text_handler_japanese.TextHandlerJapanese):
    def __init__(
        self,
        synthesis_parameters = {},
        play_sound=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.synthesis_parameters = synthesis_parameters
        self.play_sound = play_sound
        
        self.language = {
            'src': 'en',
            'dest': 'ja',
        }

    def get_output(self, text_new, args):
        speaker_id = self.synthesis_parameters['speaker_id']
        text_output = translate_google_utils.translateText(text_new, src='en', dest='ja')
        filename = f"{speaker_id}-{utils.get_timestamp()} {utils.string_parameters(self.synthesis_parameters)}.wav"
        tts_voicevox_utils.SynthesisSaveWav(text_output, speaker_id, self.synthesis_parameters, filename)
        if self.play_sound:
        	tts_voicevox_utils.playFile(filename)

        return text_output
