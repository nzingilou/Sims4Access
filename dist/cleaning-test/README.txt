S4Access cleaning test

With the game closed, copy both .ts4script files from this folder into your existing Mods/TS4_Access folder, replacing TS4_Access.ts4script. Keep your current UI packages, speech pack and settings. Restart the game.

Accessibility menu: Floor actions here opens the normal floor menu at the active Sim on their current story. Select the game vacuum action yourself. The game decides availability and cleaning scope. No mouse coordinate conversion is used.

Cleaning-state diagnostic: open Ctrl+Shift+C and run:
a11y.log on
a11y.inspect_cleaning

For a large lot: a11y.inspect_cleaning 2000. Cancel: a11y.inspect_cleaning 0. Records use the normal TS4_Access.log, prefixed cleaning inspect. Take one snapshot before cleaning a counter/toilet, clean it normally, then take another snapshot. This diagnostic does not alter objects or scanner labels.

Rollback: restore your previous TS4_Access.ts4script and remove S4Access-Cleaning-Diagnostic.ts4script, with the game closed. Restart. The previous installed main script is preserved separately in Downloads/s4access cleaning rollback.
