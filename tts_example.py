
from python_utils_aisu import utils
from . import tts_voicevox_utils
from . import translate_google_utils

def main():

  texts = [
  #   {
  #     'id': "really",
  #     'text': """
  # Really, reaally interesting!
  # So, soo exciting!
  # Quite, quiite fun!
  # Hurry hurry, we'll be late laate!
  # Study study all day, my brain is mush muush...
  # Walking walking endlessly... when will we arrive, I wonder woonder?""",
  #   },
  #   {'id': "chuuni-0", 'text': "To fret over what you cannot change is as pointless as trying to illuminate the night sky by blowing out the sun.",},
  #   {'id': "chuuni-1", 'text': "The day shall come when all we know and all we are has faded into dusk. The ultimate riddle I have to solve before that light runs out.",},
  #   {'id': "chuuni-2", 'text': "The light of truth pierces even the veil of belief - when knowledge awakens, illusion perishes. The dawn of understanding cannot be dimmed.",},
  # 	{
  # 		'id': "really ro b",
  # 		'text': """
  # リアリー・リーオーリー・イントラステング・ソー・スー・エクサイティング・クァイト・クィアイト・ファン""",
  # 	},
  # 	{
  #           'id': "really ro s",
  #           'text': """
  # リアリー リーオーリー イントラステング ソー スー エクサイティング クァイト クィアイト ファン""",
  # 	},
  # 	{
  #           'id': "really ro nos",
  #           'text': """
  # リアリーリーオーリーイントラステングソースーエクサイティングクァイトクィアイトファン""",
  # 	},
  ]

  synthesis_parameters = [
    {
      
      "speedScale": 1,
      # "pitchScale": 2,
      "intonationScale": 1,
      # "volumeScale": 0,
      # "prePhonemeLength": 0,
      # "postPhonemeLength": 0,
    },
  ]

  for speaker_id in [
    0,
    # 2,
    # 4,
    # 6,
    # 8,
    # 14,
    # 19,
    # 20,
    # 22,
    # 24,
    # 25,
    # 31,
    # 44,
    # 46,
    # 47,
    # 48,
    # 59,
  ]:
    for t in texts:
      for sp in synthesis_parameters:
        text = t['text']
        id = t['id']

        print(text)
        text = translate_google_utils.translateText(text, src='en', dest='ja')
        print(text)
        filename = f"{speaker_id}-{id} {utils.string_parameters(sp)}.wav"
        tts_voicevox_utils.SynthesisSaveWav(text, speaker_id, sp, filename)

        print(filename)
        tts_voicevox_utils.playFile(filename)


main()
