"""Namespaced reviewer HTML and a constrained JavaScript bridge."""
# ruff: noqa: E501

from __future__ import annotations

from typing import Any


class ReviewUi:
    PREFIX = "anki_speech_trainer:"

    def __init__(self, controller: Any) -> None:
        self.controller = controller

    def card_will_show(self, text: str, card: Any, kind: str) -> str:
        if kind != "reviewQuestion" or self.controller.mapping_for_card(card) is None:
            return text
        return text + _WIDGET

    def receive_js_message(
        self, handled: tuple[bool, Any], message: str, context: Any
    ) -> tuple[bool, Any]:
        if handled[0] or not message.startswith(self.PREFIX):
            return handled
        if context is not getattr(self.controller.mw, "reviewer", None):
            return handled
        action = message.removeprefix(self.PREFIX)
        if self.controller.handle_action(action):
            return (True, None)
        return handled


_WIDGET = """
<section id="ast-widget" class="ast-widget" aria-live="polite">
  <div id="ast-status" class="ast-status">Sprechen üben</div>
  <div id="ast-transcript" class="ast-transcript" hidden></div>
  <button id="ast-start" type="button">Sprechen</button>
  <button id="ast-stop" type="button" hidden>Stoppen</button>
  <button id="ast-cancel" type="button" hidden>Abbrechen</button>
</section>
<style>
.ast-widget { margin: 1em auto; max-width: 32rem; padding: .8em; border: 1px solid var(--border, #888); border-radius: .5em; }
.ast-widget button { margin: .25em; min-height: 2.4em; padding: .4em .8em; }
.ast-status, .ast-transcript { margin: .3em 0; }
</style>
<script>
window.AnkiSpeechTrainer = window.AnkiSpeechTrainer || (() => {
  const send = action => pycmd('anki_speech_trainer:' + action);
  const byId = id => document.getElementById(id);
  const update = ({state, message, transcript}) => {
    const status = byId('ast-status'); if (!status) return;
    const copy = {worker_starting: 'Spracherkennung wird geladen …', ready: 'Bereit', recording: 'Ich höre zu …', transcribing: 'Sprache wird erkannt …', match: 'Text stimmt überein', mismatch: 'Text weicht ab', uncertain: 'Nicht sicher erkannt. Bitte erneut versuchen.', error: 'Spracherkennung nicht verfügbar'};
    status.textContent = message || copy[state] || 'Sprechen üben';
    const result = byId('ast-transcript');
    result.textContent = transcript ? 'Erkannt: ' + transcript : '';
    result.hidden = !transcript;
    byId('ast-start').hidden = ['recording', 'transcribing', 'worker_starting'].includes(state);
    byId('ast-start').textContent = ['match', 'mismatch', 'uncertain', 'error'].includes(state) ? 'Erneut sprechen' : 'Sprechen';
    byId('ast-stop').hidden = state !== 'recording';
    byId('ast-cancel').hidden = !['recording', 'transcribing', 'worker_starting'].includes(state);
  };
  document.addEventListener('click', event => {
    if (event.target.id === 'ast-start') send('start');
    if (event.target.id === 'ast-stop') send('stop');
    if (event.target.id === 'ast-cancel') send('cancel');
  });
  return {update};
})();
</script>
"""
