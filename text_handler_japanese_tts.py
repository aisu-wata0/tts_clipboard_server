

from python_utils_aisu import utils
logger = utils.loggingGetLogger(__name__)
logger.setLevel('INFO')

from typing import Callable, Dict, Any, List, Optional
from pathlib import Path
import re
import threading
import queue


from text_handler.text_handler_japanese import TextHandlerJapanese
import translation_utils.tr_google
import tts.tts_utils as tts_utils
from tts.tts_utils import SoundFile
import tts.voicevox.tts_voicevox_utils as tts_voicevox_utils
from python_utils_aisu import utils, utils_japanese


class TextHandlerJapaneseTts(TextHandlerJapanese):
    def __init__(
        self,
        tts_engine: tts_utils.Tts = tts_voicevox_utils.TtsVoicevox(),
        tts_f: Callable[[str, 'TextHandlerJapaneseTts', Dict[str, Any]], str] = lambda text_new, s, args: s.tts_engine.SynthesisSaveWav(text_new, **args),
        translate_before_f: Callable[[str], str] = translation_utils.tr_google.translate,
        tts_splitter_f: Callable[[str, Dict[str, str]], tts_utils.prose_sections_type] = tts_utils.tts_splitter,
        play_sound=True,
        translate_retries=0,
        translate_fail='ignore', # 'ignore', 'cancel'
        translate=True,
        audio_output_device=None,
        audio_output_devices: Dict[str, str] = {},
        # audio_output_async: True,
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
        self.translate_retries = translate_retries
        self.translate_fail = translate_fail
        self.translate = translate
        self.audio_output_device = audio_output_device
        self.audio_output_devices = audio_output_devices

    def get_tts_args(self, t: tts_utils.prose_type):
        return utils.merge_dictionaries(
            {
                'synthesis_parameters': self.tts_engine.synthesis_parameters,
            },
            t['tts_args'],
        )

    def play_prose_section(self, t, content_key, t_prev=None, audio_output_device=None):
        tts_content = t[content_key]
        logger.info(f"tts content `{tts_content}`")
        voiced_match = utils_japanese.re_voiced_plus_c.search(tts_content)
        if voiced_match:
            filepath = None
            try:
                tts_args = self.get_tts_args(t)
                filepath = self.tts_f(
                    tts_content, self, tts_args)
            except Exception as e:
                logging.exception(f"While creating sound file {t}")
            
            if filepath:
                # Calculate the delay based on the change of t['type']
                delay = 0
                if t_prev and t_prev['type'] != t['type']:
                    # Add a 1-second delay for the change from narration to dialogue
                    delay = 1 
                
                return SoundFile(filepath, delay, device=audio_output_device)

    def get_output(self, text_new, args):
        logger.info(f"get_output {text_new}")
        text_new = self.text_preprocess(text_new, args)
        audio_output_device = self.audio_output_device

        prose_sections = self.tts_splitter_f(text_new, self.tts_engine.speakers)
        logger.info(f"prose_sections {prose_sections}")
        
        file_queue: Optional[queue.Queue[SoundFile]] = None
        if self.play_sound:
            file_queue = queue.Queue()

            # Create a separate thread for playing files
            file_thread = threading.Thread(
                target=tts_utils.play_files_from_queue, args=(file_queue,))
            file_thread.daemon = True
            file_thread.start()
        
        t_prev = None
        for t in prose_sections:
            if not self.translate:
                t['content_translation'] = t['content']
            else:
                translate_retries = self.translate_retries
                while True:
                    try:
                        t['content_translation'] = self.translate_before_f(t['content'], **self.language)
                        break
                    except:
                        if translate_retries <= 0:
                            logging.info(f"Failed translation for {t['content']}")
                            t['content_translation_fail'] = True
                            if self.translate_fail == 'ignore':
                                t['content_translation'] = t['content']
                            elif self.translate_fail == 'cancel':
                                t['content_translation'] = ""
                            break
                        translate_retries -= 1

            t['content_translation_post_process'] = self.text_postprocess(
                t['content_translation'], args).strip()

            if file_queue:
                content_key = 'content_translation_post_process'
                
                device_ = audio_output_device
                if  t['type'] in self.audio_output_devices:
                    device_ = self.audio_output_devices[t['type']]
                
                f = self.play_prose_section(
                    t, content_key, t_prev, audio_output_device=device_)
                if f:
                    file_queue.put(f)
            
            t_prev = t

        if file_queue:
            # Wait for all files in the queue to be played
            self.wait = file_queue
        
        return tts_utils.prose_sections_to_text(prose_sections, 'content_translation_post_process')
