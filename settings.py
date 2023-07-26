

port = 50022
url = '127.0.0.1'

# Inputs
clipboardWatcher = True
httpServer = True


from text_handler_japanese_tts import TextHandlerJapaneseTts

ClipboardWatcher_args = {
	'queue_text_events': False,
	'cooldown': 0.01,
}


from translation_utils import tr_google

from tts.vits.tts_vits_utils import TtsVits
from tts.voicevox.tts_voicevox_utils import TtsVoicevox


# "Sound device 'None' is default, < 0 is disabled"
# "Sound devices are listed when you run the server
# "Base sound device"
tts_audio_output_device = None
# "Specific sound devices"
tts_devices = {
    'narration': None,
    'dialogue': None,
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

from SentimentAnalysis.sentiment_analysis import SentimentClassifier

# Hardcoded
sentiment_classifier = None
# try:
#     sentiment_classifier = SentimentClassifier()
# except Exception as e:
#     print(f"{e}")
#     print("FAILED TO LOAD SENTIMENT CLASSIFIER")


tts_handler = TextHandlerJapaneseTts(**{
    'characters_to_spaces': ['_'],
   	'camelcase_to_spaces': True,
   	'english_to': 'engrish',
	'translate_before_f': tr_google.translate,
	'tts_engine': tts_engine,
	# 'tts_engine': Voicevox(),
	'sentiment_classifier': sentiment_classifier,
	'audio_output_device': tts_audio_output_device,
	'audio_output_devices': tts_devices,
	# 'movement_url': "http://127.0.0.1:{port}/movement".format(port=7880),
	'character_name': character_name,
})

