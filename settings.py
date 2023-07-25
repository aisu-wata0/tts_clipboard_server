

port = 50022
url = '127.0.0.1'

# Inputs
clipboardWatcher = False
httpServer = True


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

character_name = 'Aria'

tts_engine = TtsVits(
	port = 7860,
	url = "http://127.0.0.1:{port}/run/tts-{speaker_id}",
	soundfile_dir = "soundfiles",
	speakers = {
		# 'narration': "Shiromi Iori",
		# 'narration': "Tendou Alice",
		'narration': "Misono Mika",
		'dialogue': "herta",
		'speaker-default': "Shiromi Iori",
		'default': "Misono Mika",
        character_name: 'Tendou Alice',
	},
	synthesis_parameters = {
		#   "content": "",
		#   # : string
		'Language': "Japanese",
		#  : string
		'noise_scale': 0.6,
		#  : number
		'noise_scale_w': 0.668,
		#  : number
		'length_scale': 1,
		#  : number
		'Symbol input': False,
		#  : boolean
	},
)

tts_handler = TextHandlerJapaneseTts(**{
    'characters_to_spaces': ['_'],
   	'camelcase_to_spaces': True,
   	'english_to': 'engrish',
	'translate_before_f': tr_google.translate,
	'tts_engine': tts_engine,
	# 'tts_engine': Voicevox(),
	'audio_output_device': 11,
	'audio_output_devices': devices,
	'movement_url': "http://127.0.0.1:{port}/movement".format(port=7880),
	'character_name': character_name,
})

