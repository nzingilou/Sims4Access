# Developer manifest

Base: upstream adb868c. CHANGES.patch is cumulative and reverse-checked. changed-source contains only differing source files; SOURCE-MANIFEST.json lists hashes and deletions.

Speech update: Scripts/tyjokr_a11y_speech_process.py (SpeechJob) provides native kill-on-close ownership. speech.py (_try_init_sapi, _dispose_sapi_locked, restart_sapi, stop, _speak_now) serializes lifecycle access, closes/reaps the child and registers optional normal-exit cleanup. tools/test_speech_process_lifecycle.py covers ten cases, including actual Windows parent exit/crash.

Other changes are grouped in changed-source/contrib-reference/docs/DEVELOPER-MANIFEST.md. Compiled script contains the complete current mod. Main/compatibility UI packages are the matching November test pair.
