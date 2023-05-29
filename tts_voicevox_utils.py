
from pathlib import Path
import urllib.request
import urllib.parse
import urllib
import requests
import winsound

from python_utils_aisu import utils
import tts_voicevox_settings

def playFile(filename):
  winsound.PlaySound(filename, winsound.SND_FILENAME)

class Voicevox:
  def __init__(
      self,
      url=tts_voicevox_settings.url,
      port=tts_voicevox_settings.port,
      speaker_id=tts_voicevox_settings.speaker_id,
      synthesis_parameters=tts_voicevox_settings.synthesis_parameters,
      soundfile_dir=tts_voicevox_settings.soundfile_dir,
  ) -> None:
    self.speaker_id = speaker_id
    self.url = url
    self.port = port
    self.synthesis_parameters = synthesis_parameters
    self.soundfile_dir = soundfile_dir

  def get_url(self):
    return self.url.format(port=self.port)
  
  def get_filepath(self):
    return f"{self.soundfile_dir}/{self.speaker_id}-{utils.get_timestamp()} {utils.string_parameters(self.synthesis_parameters)[:80]}.wav"

  def Synthesis(self, text, speaker_id=None, synthesis_parameters={}):
    if speaker_id is None:
      speaker_id = self.speaker_id
    synthesis_parameters = {**self.synthesis_parameters, **synthesis_parameters}
    params_encoded = urllib.parse.urlencode({'text': text, 'speaker': speaker_id})
    response = requests.post(f'{self.get_url()}/audio_query?{params_encoded}')
    params_encoded = urllib.parse.urlencode({'speaker': speaker_id, 'enable_interrogative_upspeak': True})
    synthesis_request = response.json()
    for k in synthesis_parameters.keys():
      synthesis_request[k] = synthesis_parameters[k]

    synthesis_res = requests.post(f'{self.get_url()}/synthesis?{params_encoded}', json=synthesis_request)
    return synthesis_res


  def SynthesisSaveWav(self, text, filepath=None, speaker_id=None, synthesis_parameters={}):
    if filepath is None:
      filepath = self.get_filepath()
    synthesis_res = self.Synthesis(
        text, speaker_id, synthesis_parameters)
    return self.SynthesisResponseSaveWav(synthesis_res, filepath)


  def SynthesisResponseSaveWav(self, synthesis_res, filepath=None):
    if filepath is None:
      filepath = self.get_filepath()
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as outfile:
      outfile.write(synthesis_res.content)
    return filepath
