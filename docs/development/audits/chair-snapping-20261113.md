# Native chair-slot findings

Game 1.129.39.1030: objects.slots.SlotType tuning explicitly describes Build/Buy slots for chairs. SlotComponent.get_runtime_slots_gen yields native part-owned RuntimeSlots. RuntimeSlot.is_valid_for_placement delegates to build_buy.test_location_for_object; add_child supplies the slot's transform and hash to set_parent. The restaurant seating lookup identifies chairs through table-part children.

The implementation uses these native slots for dining and desk chairs, with no guessed offsets or yaw. Preview validates the definition; the ordinary native tool-drop acknowledgement precedes object validation. Table, seat, zone, product, cursor and focus are rechecked. Parent/hash/child membership is verified before and after Build/Buy registration, before payment. Full/refused/stale seats never fall back to buying a floor chair. The native-slot helper is independent of orientation hints and has its own experimental setting.

Offline transaction tests cover rejection, stale state, occupied seats, native part/root duplicates, failed parenting and failed payment. Live-game snapping remains pending testing.
