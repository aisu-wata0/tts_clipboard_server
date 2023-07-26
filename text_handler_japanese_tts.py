

from dataclasses import dataclass
from python_utils_aisu import utils
logger = utils.loggingGetLogger(__name__)
logger.setLevel('INFO')

from typing import Callable, Dict, Any, List, Optional
from pathlib import Path
import re
import threading
import time
import queue
import requests


from text_handler.text_handler_japanese import TextHandlerJapanese
import translation_utils.tr_google
import tts.tts_utils as tts_utils
from tts.tts_utils import SoundFile
import tts.voicevox.tts_voicevox_utils as tts_voicevox_utils
from python_utils_aisu import utils, utils_japanese
from SpeechToMouthShape import vits_japanese

from SentimentAnalysis.sentiment_analysis import SentimentClassifier

@dataclass
class TTSEvent:
    soundfile: SoundFile
    sentiments: Dict[str, float] | None = None
    mouth_keyframes: Dict[float, str] | bool | None = None
    movement_url: str | None = None

    def __post_init__(self):
        if isinstance(self.mouth_keyframes, bool):
            if self.mouth_keyframes:
                self.set_mouth_keyframes()

    def play(self, delete_file=True):
        self.soundfile.read()
        if self.soundfile.delay > 0:
            logger.info(f"self.soundfile.delay {self.soundfile.delay}")
            time.sleep(self.soundfile.delay)
        movement_thread = None
        if self.movement_url is not None and (self.mouth_keyframes or self.sentiments):
            data = {}
            if not isinstance(self.mouth_keyframes, bool):
                data['mouth_keyframes'] = self.mouth_keyframes
            if isinstance(self.sentiments, dict):
                data['sentiments'] = self.sentiments
            
            movement_url = self.movement_url
            def movement_request_():
                requests.post(url=movement_url, json=data, timeout=1)
                logger.info("movement_request_ done", data)
            movement_thread = threading.Thread(
                target=movement_request_,
                # target=requests.post,
                # kwargs=dict(url=movement_url, json=data, timeout=1),
                daemon=True,
            )
            movement_thread.start()
            # requests.post(self.movement_url, json=data)
        
        logger.info(f"Playing file {self.soundfile.filepath} at device {self.soundfile.device}")
        self.soundfile.play(delete_file=delete_file)
        if movement_thread:
            movement_thread.join()

    def set_mouth_keyframes(self):
        self.mouth_keyframes = vits_japanese.filepathToKeyframes(self.soundfile.filepath)
        logger.info(f"TTSEvent.set_mouth_keyframes {self.mouth_keyframes}")

    def process(self, mouth_keyframes=True):
        if mouth_keyframes:
            self.set_mouth_keyframes()


def play_TTSEvents_from_queue(file_queue: "queue.Queue[TTSEvent | None]"):
    while True:
        logger.info(f"TSEvents_from_queue: Waiting file")
        event = file_queue.get()
        if not event:
            logger.info(f"TSEvents_from_queue: Ending")
            file_queue.task_done()
            return
        event.play()
        file_queue.task_done()



class TextHandlerJapaneseTts(TextHandlerJapanese):
    def __init__(
        self,
        tts_engine: tts_utils.Tts = tts_voicevox_utils.TtsVoicevox(),
        tts_f: Callable[[str, 'TextHandlerJapaneseTts', Dict[str, Any]], str] = lambda text_new, s, args: s.tts_engine.SynthesisSaveWav(text_new, **args),
        translate_before_f: Callable[[str], str] = translation_utils.tr_google.translate,
        tts_splitter_f: Callable[[str, Dict[str, str]], List[tts_utils.prose_type]] = tts_utils.tts_splitter,
        play_sound=True,
        translate_retries=0,
        translate_fail='ignore', # 'ignore', 'cancel'
        translate=True,
        audio_output_device=None,
        audio_output_devices: Dict[str, str] = {},
        tts_delay_type_change = 0.5,
        movement_url=None,
        character_name: str = "",
        sentiment_classifier: SentimentClassifier | None = None,
        # audio_output_async: True,

        # # TextHandlerJapanese
        print_romaji=True,
        characters_to_spaces=['_'],
        camelcase_to_spaces=True,
        english_to='engrish', # 'katakana' or 'engrish'
        *args,
        **kwargs,
    ):
        kwargs = utils.merge_dictionaries(*[
            {
                'language': {
                    'src': 'auto',
                    'dest': 'ja',
                }
            },
            kwargs,
        ])
        super().__init__(
            print_romaji=print_romaji,
            characters_to_spaces=characters_to_spaces,
            camelcase_to_spaces=camelcase_to_spaces,
            english_to=english_to,
            *args,
            **kwargs,
        )
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
        self.tts_delay_type_change = tts_delay_type_change
        self.movement_url = movement_url
        self.character_name = character_name
        self.sentiment_classifier = sentiment_classifier

    def get_tts_args(self, t: tts_utils.prose_type):
        return utils.merge_dictionaries(
            {
                'synthesis_parameters': self.tts_engine.synthesis_parameters,
            },
            t['tts_args'],
        )

    def play_prose_section(
        self,
        t: Dict[str, Any],
        content_key: str,
        t_prev=None,
        content_key_sentiments: str | None=None,
        mouth_keyframes: Dict[float, str] | bool | None = None,
        audio_output_device: str | None =None
    ):
        if (
            (isinstance(audio_output_device, int) and audio_output_device < 0) or 
            (isinstance(audio_output_device, str) and not audio_output_device)
        ):
            return None
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
                logger.exception(f"While creating sound file {t}")
            
            if filepath:
                # Calculate the delay based on the change of t['type']
                delay = 0
                if t_prev and t_prev['type'] != t['type']:
                    # Add a delay for the change from narration to dialogue
                    delay = self.tts_delay_type_change
                
                mouth_keyframes = False
                sentiments = {}
                if 'name' in t and (self.character_name.lower() == t['name'].lower()):
                    mouth_keyframes = True
                    if content_key_sentiments:
                        if self.sentiment_classifier:
                            sentiments = self.sentiment_classifier.get(t[content_key_sentiments])
                            print(f"content_key_sentiments {content_key_sentiments} sentiments:")
                            for k, v in sentiments.items():
                                print(k, v)
                            print()
                return TTSEvent(
                    SoundFile(filepath, delay, device=audio_output_device),
                    sentiments=sentiments,
                    mouth_keyframes=mouth_keyframes,
                    movement_url=self.movement_url,
                )

    def get_output(self, text_new, args):
        logger.info(f"get_output() {text_new}")
        text_new = self.text_preprocess(text_new, args)
        audio_output_device = self.audio_output_device

        prose_sections = self.tts_splitter_f(text_new, self.tts_engine.speakers)
        for p in prose_sections:
            logger.info(f"prose_section {p}")
        
        tts_queue: Optional[queue.Queue[TTSEvent | None]] = None
        if self.play_sound:
            tts_queue = queue.Queue()

            # Create a separate thread for playing files
            file_thread = threading.Thread(
                target=play_TTSEvents_from_queue, args=(tts_queue,))
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
                            logger.info(f"Failed translation for {t['content']}")
                            t['content_translation_fail'] = True
                            if self.translate_fail == 'ignore':
                                t['content_translation'] = t['content']
                            elif self.translate_fail == 'cancel':
                                t['content_translation'] = ""
                            break
                        translate_retries -= 1
            
            logger.info(f"content_translation: {t['content_translation']}")
            t['content_translation_post_process'] = self.text_postprocess(
                t['content_translation'], args).strip()
            logger.info(f"content_postprocess: {t['content_translation_post_process']}")

            if tts_queue:
                content_key = 'content_translation_post_process'
                
                device_ = audio_output_device
                if  t['type'] in self.audio_output_devices:
                    device_ = self.audio_output_devices[t['type']]
            
                f = self.play_prose_section(
                    t, content_key, t_prev, content_key_sentiments=self.get_content_key_en(t), audio_output_device=device_)
                if f:
                    tts_queue.put(f)
            
            t_prev = t

        if tts_queue:
            # To kill the thread
            tts_queue.put(None)
            # Wait for all files in the queue to be played
            self.wait = tts_queue
        
        return tts_utils.prose_sections_to_text(prose_sections, 'content_translation_post_process')

    def get_content_key_en(self, t):
        k = 'content'
        if self.language['dest'] == 'en':
            k = 'content_translation'
        return k
            