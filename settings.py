

port = 50022
url = '127.0.0.1'

import tts_voicevox_settings as tts_voicevox

ClipboardWatcher_args = {
	'queue_text_events': False,
	'cooldown': 0.01,
}

TextHandler_args = {
    'characters_to_spaces': ['_', '-'],
	'camelcase_to_spaces':True,
	'english_to_katakana':True,
}
