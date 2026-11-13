# Chair snapping audit

Current chair_alignment adds direction hints only. Grid floor placement checks fit; it does not verify a usable chair/table pair. Explicit focused-surface placement accepts only native compatible empty runtime slots, but chair snapping through that path is not established.

The installed Python exposes RestaurantZoneDirector.get_dining_table_by_chair, a read-only restaurant seating lookup, not a general Build placement operation. A dedicated chair assistant still needs a verified native placement path and post-placement seating-link checks. No chair-snapping behavior is added in this update.
