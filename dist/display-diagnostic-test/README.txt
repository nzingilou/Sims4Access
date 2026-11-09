Read-only display diagnostic

With the game closed, back up Mods/TS4_Access/TS4_Access.ts4script and replace it with this file.

Enter Build Mode. Open the cheat console and run:
a11y.log on
a11y.inspect_display 5
Close the console and keep the game focused for five seconds. Records appear in TS4_Access.log under "display inspect:".

The command takes Windows measurements without moving a pointer, requesting a game projection or constructing anything. It also enables passive logging of later user-initiated builder projections/conversions on their actual worker thread. Logging is capped at 30 observations per minute and respects a11y.log off.

The game UI-stage size remains unknown; current client/adapter dimensions and saved display settings are labelled separately. A manual snapshot alone does not validate game projection units. The diagnostic preserves the installed coordinate conversion for measurement.

The developer-source folder contains only changed sources. CHANGES.patch and SOURCE-MANIFEST.json record the exact source delta.
