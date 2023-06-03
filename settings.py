

port = 50022
url = '127.0.0.1'

from text_handler_japanese_tts import TextHandlerJapaneseTts

ClipboardWatcher_args = {
	'queue_text_events': False,
	'cooldown': 0.01,
}


from translation_utils import tr_google

from tts.vits.tts_vits_utils import TtsVits
from tts.voicevox.tts_voicevox_utils import TtsVoicevox

devices = {
    'narration': None,
    'dialogue': 11,
    'speaker-default': None,
    'default': None,
}

tts_handler = TextHandlerJapaneseTts(**{
    'characters_to_spaces': ['_'],
   	'camelcase_to_spaces': True,
   	'english_to': 'engrish',
	'translate_before_f': tr_google.translate,
	'tts_engine': TtsVits(),
	# 'tts_engine': Voicevox(),
	'audio_output_device': 11,
	'audio_output_devices': devices,
})

