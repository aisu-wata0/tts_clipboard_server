from pathlib import Path
import threading
import json
import logging

from python_utils_aisu import utils, utils_japanese

from text_handler import text_handler_japanese
import translate_google_utils
import tts_voicevox_utils
import tts_voicevox_settings

class TextHandlerJapaneseTtsVoicevox(text_handler_japanese.TextHandlerJapanese):
    def __init__(
        self,
        Voicevox_args = {         
            'url': tts_voicevox_settings.url,
            'port': tts_voicevox_settings.port,
            'speaker_id': tts_voicevox_settings.speaker_id,
            'synthesis_parameters': tts_voicevox_settings.synthesis_parameters,
        },
        play_sound=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.play_sound = play_sound
        
        self.language = {
            'src': 'en',
            'dest': 'ja',
        }
        self.voicevox = tts_voicevox_utils.Voicevox(
             **Voicevox_args,
        )

    def get_output(self, text_new, args):
        text_new = super().get_output(text_new, args)

        text_output = translate_google_utils.translateText(text_new, src='en', dest='ja')
        filepath = ""
        try:
            if self.play_sound:
                filepath = self.voicevox.SynthesisSaveWav(text_output)
                tts_voicevox_utils.playFile(filepath)
        except Exception as e:
            logging.exception(f"While playing {filepath}")
        finally:
            Path(filepath).unlink()


        return text_output
