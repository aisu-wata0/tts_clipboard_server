import logging
from typing import Callable, Dict, Any, List
from pathlib import Path


from text_handler.text_handler_japanese import TextHandlerJapanese
import translation_utils.tr_google
import tts.tts_utils as tts_utils
import tts.voicevox.tts_voicevox_utils as tts_voicevox_utils
from python_utils_aisu import utils


class TextHandlerJapaneseTts(TextHandlerJapanese):
    def __init__(
        self,
        tts_engine: tts_utils.Tts = tts_voicevox_utils.TtsVoicevox(),
        tts_f: Callable[[str, 'TextHandlerJapaneseTts', Dict[str, Any]], str] = lambda text_new, s, args: s.tts_engine.SynthesisSaveWav(text_new, **args),
        translate_before_f: Callable[[str], str] = translation_utils.tr_google.translate,
        tts_splitter_f: Callable[[str, Dict[str, str]], tts_utils.prose_sections_type] = tts_utils.tts_splitter,
        play_sound=True,
        *args,
        **kwargs,
    ):
        kwargs = utils.merge_dictionaries(*[
            {
                'language': {
                    'src': 'en',
                    'dest': 'ja',
                }
            },
            kwargs,
        ])
        super().__init__(*args, **kwargs)
        self.tts_engine = tts_engine
        self.tts_f = tts_f
        self.translate_before_f = translate_before_f
        self.tts_splitter_f = tts_splitter_f
        self.play_sound = play_sound

    def get_tts_args(self, t: tts_utils.prose_type):
        return utils.merge_dictionaries(
            {
                'synthesis_parameters': self.tts_engine.synthesis_parameters,
            },
            t['tts_args'],
        )

    def get_output(self, text_new, args):
        text_new = self.text_preprocess(text_new, args)

        prose_sections = self.tts_splitter_f(text_new, self.tts_engine.speakers)
        print("prose_sections")
        print(prose_sections)
        for t in prose_sections:
            t['content-translation'] = self.translate_before_f(t['content'], **self.language)

            t['content-translation-post_process'] = self.text_postprocess(
                t['content-translation'], args)

            if self.play_sound:
                filepath = None
                try:
                    tts_args = self.get_tts_args(t)
                    filepath = self.tts_f(
                        t['content-translation-post_process'], self, tts_args)
                    tts_utils.playFile(filepath)
                except Exception as e:
                    logging.exception(f"While playing {filepath}")
                finally:
                    try:
                        if filepath and Path(filepath).exists():
                            Path(filepath).unlink()
                    except Exception as e:
                        logging.exception(f"While deleting {filepath}")

        return tts_utils.prose_sections_to_text(prose_sections, 'content-translation-post_process')
