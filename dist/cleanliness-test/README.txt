Scanner cleanliness test build

With the game closed, back up Mods/TS4_Access/TS4_Access.ts4script and replace it with this script.

Scanner announcements add dirty or dusty when the object's verified native state reports that condition. Dirt and dust are distinct. A clean object has no added suffix. Repeat after cleaning to hear the current state; no manual rescan should be needed for the suffix itself.

Test the dirty toilet and a clean sink, then clean the toilet normally and repeat its scanner announcement. The snapshot also identified a dusty desk; that should say dusty rather than dirty. State-read failures use the log marker "cleanliness:" when mod logging is enabled.

The developer-source folder contains only changed sources. CHANGES.patch and SOURCE-MANIFEST.json identify the starting revision and exact changes.
