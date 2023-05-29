
import urllib.request
import winsound
import urllib.parse
import urllib
import requests

from . import tts_voicevox_settings


def Synthesis(text, speaker_id, synthesis_parameters=tts_voicevox_settings.synthesis_parameters_defaults):
  params_encoded = urllib.parse.urlencode({'text': text, 'speaker': speaker_id})
  response = requests.post(f'{tts_voicevox_settings.voice_vox_url}/audio_query?{params_encoded}')
  params_encoded = urllib.parse.urlencode({'speaker': speaker_id, 'enable_interrogative_upspeak': True})
  synthesis_request = response.json()
  for k in synthesis_parameters.keys():
    synthesis_request[k] = synthesis_parameters[k]

  synthesis_res = requests.post(f'{tts_voicevox_settings.voice_vox_url}/synthesis?{params_encoded}', json=synthesis_request)
  return synthesis_res


def SynthesisSaveWav(text, speaker_id, synthesis_parameters, filename):
  synthesis_res = Synthesis(text, speaker_id, synthesis_parameters)
  SynthesisResponseSaveWav(synthesis_res, filename)

def SynthesisResponseSaveWav(synthesis_res, filename):
  with open(filename, "wb") as outfile:
    outfile.write(synthesis_res.content)

def playFile(filename):
	winsound.PlaySound(filename, winsound.SND_FILENAME)