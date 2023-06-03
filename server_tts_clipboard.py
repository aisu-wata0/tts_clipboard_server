
#! python

import logging
from python_utils_aisu import utils

logger = utils.loggingGetLogger(__name__)
logger.setLevel('INFO')
utils.loggingSetFormatter()

import threading
import json
from datetime import datetime
from typing import Union
from collections.abc import Iterable

import sounddevice as sd

import clipboard_event.clipboard_watcher as clipboard_watcher
import translation_utils.filters

import settings

tts_handler = settings.tts_handler

def text_thread(text):
    thread = threading.Thread(
        target=tts_handler.handle, args=(text,))
    return thread


from flask import Flask, request

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARN)
app = Flask(__name__)
translation = ""


@app.route('/tts', methods=['GET'])
def route_tts():
    text = request.args.get('text')
    if isinstance(text, str):
        # replace this with your actual translation function
        translation = tts_handler.handle(text)
        return translation


def run_flask():
    app.run()


from werkzeug.serving import make_server


class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server(settings.url, settings.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


if __name__ == "__main__":
    import argparse
    # Instantiate the parser
    parser = argparse.ArgumentParser(
        description='TTS Server, but it also TTS any clipboard text\n'
        'python ' + __file__ + ' ',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose')

    # Parse arguments
    args = parser.parse_args()

    print(sd.query_devices())

    print(f"Watching clipboard.", flush=True)
    print(f"Keys:", flush=True)
    print(f"\t'q': Quit", flush=True)
    print(f"\t'p': Pause", flush=True)
    print(f"\t'u': Unpause", flush=True)
    print(f"\t'c': Clear history", flush=True)
    print(f"\t'int': Delete last `int` entries from history", flush=True)

    # wait for links in clipboard
    def predicate(text):
        # this can filter new text if you want
        # just return empty when you don't want to translate it
        text = translation_utils.filters.filter_fix_nl(text)
        logger.info(f"```translation_utils.filters.filter_code_blocks\n{text}\n```")
        text = translation_utils.filters.filter_code_blocks(text, "[... code block]")
        logger.info(f"```translation_utils.filters.filter_code_blocks\n{text}\n```")
        return text

    watcher = clipboard_watcher.ClipboardWatcher(
        predicate, text_thread, **settings.ClipboardWatcher_args,)

    watcher.start()

    # flask_thread = ServerThread(app)
    flask_thread = None
    # flask_thread.start()
    temperature = 0.4

    while True:
        try:
            inp = input("...")
            inp = inp.lower()
            # # Keybindings
            # Pause
            if inp == "p":
                print('pausing...', flush=True)
                watcher.pause()
            # Unpause
            if inp == "u":
                print('continuing...', flush=True)
                watcher.unpause()
            # Clear history
            if inp == "c":
                print('clearing history...', flush=True)
                tts_handler.clear_history(len(tts_handler.history))
            if inp == "reload_settings":
                print(f"reload_settings")
                # TODO: reload and set text handler settings
                utils.reload_lib(settings)
            # Retry translation
            if inp == "r":
                tts_handler.retry_last()
            # Show history
            if inp == "s":
                print(
                    f'Showing history... length = {len(tts_handler.history)} how far back (int)?', flush=True)
                show_qnt = input("...")
                if not show_qnt.isdigit():
                    print(f'Invalid number {show_qnt}', flush=True)
                    continue
                try:
                    for (o, t) in zip(tts_handler.history[-int(show_qnt):], tts_handler.history_output[-int(show_qnt):]):
                        print("")
                        print(o)
                        print("")
                        print(t)
                except Exception as e:
                    logger.exception("Exception while printing history")
            if inp.isdigit():
                tts_handler.clear_history(inp)
            # Quit / Break out
            if inp == "q":
                break
            # #
        except KeyboardInterrupt:
            print("Clipboard watcher interrupted.")
            break
        except Exception as e:
            logger.exception(
                f"Caught exception while waitning for user input")
            pass

    print('stopping...', flush=True)
    tts_handler.save_state(True)
    watcher.stop()
    watcher.join()

    if flask_thread:
        flask_thread.shutdown()
