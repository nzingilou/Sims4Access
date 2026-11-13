# UI port: game 1.129.39.1030

Current EA UI SHA256: `6807e477012eca956ee8ef744c00917d4f983547826a0af5c741391e94d0ac83`.
The 1.128 reference snapshot remains unchanged. Work in progress; no new package deployed.
Local extracted inputs and complete-package class ownership: `build/transfer-audit/current-inputs.json`.
Current-source exports and diffs: `build/ui-port/current-sources/` (not distributable).

## Movie progress

All 25 current-game inputs were checked against the installed UI, targeted native classes compared, existing hooks retained, and movies rebuilt serially. The full fidelity gate passed 62 targeted-class comparisons. Exact non-code tags and class sets are preserved in every movie. Runtime testing remains separate.

| Movie | Native port / compile / offline gate |
| --- | --- |
| SimInfoMotivePanel | Pass |
| SimInfoTray | Pass |
| ClassLibraryGamedata | Pass |
| PickersPurchase | Pass |
| Pickers | Pass |
| Dialog | Pass |
| UIContainer | Pass |
| AgeUpPanel | Pass |
| BaseLibrary | Pass |
| ClassLibraryOlympus | Pass |
| ClassLibraryScaleform | Pass |
| ClassLibraryWidgetsShared | Pass |
| ComponentLibrary | Pass |
| GUIComponentLibrary | Pass |
| GameEntryDock | Pass |
| GameEntryLauncher | Pass |
| GameEntryLibrary | Pass |
| GameTray | Pass |
| HUDLibrary | Pass |
| InteractionQueue | Pass |
| Notifications | Pass |
| ObjectBoundElements | Pass |
| PieMenu | Pass |
| SimHub | Pass |
| TimeControls | Pass |

Regression suite including the purchase follow-up: **passed**, **input_stable true**, 1,497 reported checks across 111 isolated suites (includes repeated imported checks). Static message inventory: 35 registered messages, no missing handler methods, no unmatched literal Flash speech commands; Repeat and SpeechMode are Python-local controls.

Handler audit: 39 routing/activation methods match the Git base source and have matching normalized instructions, jump destinations and exception ranges across all 29 patched TooltipManager copies. Game Python modules and contribution modules match the Git base. The updated purchase-footer helper was separately verified in all 29 copies. The nine-case scanner pick bridge fixture exercises encoded picks through `A11yOpenPieMenu` to `interactions.choices`, including large IDs, Sim picks, native-message forwarding, mode changes and request-ID rollover. The current native EA pie menu retains the same 14-argument interaction request layout.

Compatibility: six current UI Cheats inputs compared and rebuilt; fidelity gate passed 19 targeted-class comparisons. Exact non-code tags and class sets are preserved in all six.

## Changes

Purchase follow-up: the log's Romantic Items cart remained at count/cost zero while Enter moved from the Sweetheart's Box row to disabled Done. Current EA `PurchasePicker.CheckCost` requires a nonempty cart and sufficient funds. `A11yPickerFooter` now retains row focus when Done is disabled, reads its native funds reason or the native empty-cart text, and announces Left/Right quantity controls. Native quantity, affordability and confirmation actions are preserved. Its nine-case fixture covers empty carts, funds, enabled confirmation, teardown, recipe Next, the quantity-to-confirmation sequence and game-disabled increases. The diagnostic marker is `purchase-footer-disabled`. Fresh full rebuild/gate reports are under `build/purchase-fix/`.

- `flash/extra-classes/CommodityContainer.as`, `A11yMotiveText`: use EA's trait-dependent `GetCommodityName(AllTraitIds)` like the displayed title. Clamp percentages and omit invalid numeric values. Existing speech channel retained.
- `tools/ui_port_inventory.py`: verify all 25 inputs against the installed UI and find actual class definitions across the complete package.
- `tools/ui_port_sources.py`: export targeted source one movie at a time and retain diffs for manual review.
- `tools/test_occult_motive_text.js`: exercise actual narration method with trait-dependent names, normal/range limits and invalid values.
- `flash/TooltipManager_patched.as`, `A11yInformational`: expose the native occult rank/points rows while retaining their powers button. `A11yCompositeRow`: traverse native perk-rank and transfer-neighborhood wrappers to reach their actual buttons and visible nested choices. No new message or purchase service introduced.
- `flash/extra-classes/DialogMain.as`, `HandleShowSavingDialog`: retain current EA `allowDuringLoading` behavior during the port.
- `flash/prepare_uicheats_purchase.py` and `build_uicheats_compat.ps1`: generate a compatibility-only cart cell preserving UI Cheats v1.59.1 right-click ten-item quantity changes and the shared narration hooks. `-BaseDir` accepts isolated reviewed inputs; the compatibility gate accepts the same path through `TS4_UICHEATS_BASE`.
- `tools/ui_bridge_inventory.py`: record registered messages, handler methods, speech commands and local Python speech controls.
- `tools/ui_port_verify.py`: compare class sets and exact non-code tags across the complete rebuild.
- `tools/ui_port_handler_audit.py` and `tools/test_scanner_pick_bridge.js`: compiled handler parity and scanner-to-pie callback regression protection. Pcode normalization removes debug metadata and private script numbering, and maps byte offsets to instruction positions while preserving branches and exception ranges.

## Narrow follow-up investigations

- Simology rank/powers controls and PerksPanel are outside the 25 shipped movies. Prefer safe shared-manager traversal using native buttons; do not introduce whole-movie overrides without separately reviewing their risk and UI Cheats overlap.
- Current `MotivePanelRankedStatContent` uses `GetDataByOccultType` for the needs-panel occult rank/powers section. `SummaryPanelRankedStatContent.Setup` uses ghost-powers data in Simology. The shared-manager additions follow those existing sections rather than inventing a second werewolf abilities menu in Simology.
- EngagementLibrary was previously associated with a freeze when opening Gallery; it is not evidence of Gallery ownership. Current class definitions place Gallery details/filters in ExchangeDetail/ExchangeLibrary. Do not re-enable the EngagementLibrary override.
- Current Gallery details are in `ExchangeDetail`: `DetailInfoCellView.mcDescriptionInfo` and `txtDescriptionEdit.CurrentText` expose descriptions. `SetupDescriptionInfo` switches editability, so a read-only description stop must avoid entering editing mode. The generic collector caps a row at 24 text entries; test whether metadata crowds out the description before changing it. Native ExchangeDetail export reports unresolved PlaceObject3 tags: retain the original movie.
- Current Gallery filters are in `ExchangeLibrary`: `FilterOptionsGroup` exposes `txtLabel`, `txtContextInfo`, `mcGridView`, and `btnExpand`; `GalleryFilterCheckboxButton` has native checkbox state. A focused follow-up should add group context without repeating checkbox text or disturbing collapsed/locked filters.
- TimeControlsMain is defined in SimHub and TimeControls. Compare both native bodies before choosing a patch strategy.
- Alt+N uses a fixed six-need Python list. Do not guess occult stat IDs or treat all meters as “low is bad”; prefer current UI data and game tuning.
- Manage Worlds transfer-neighborhood wrapper traversal is fixed in source; nested grid/native selection-event behavior still requires in-game testing. Successful transfers in earlier logs do not establish all routes work.
- Standard and UI Cheats compatibility targets confirmed. Publish to the fork and Downloads only; do not replace installed game files. Current UI Cheats v1.59.1 replaced-class differences were reviewed: clock attachment and right-click cart quantity handling are preserved.
- Existing four contribution fixture scripts printed uncounted success messages; their summaries now report one scenario each so the full runner can recognize them. No assertions changed. Build the helper executable before the complete suite, as required by the developer build instructions.

## Release requirements

The complete offline suite, literal bridge inventory, standard/compatibility fidelity gates and movie structure checks passed. Package identity checks follow assembly. The checkout has no `.handoff/baseline.json`, so `Dev.ps1 return` cannot create its old-format archive; the review patch is anchored to Git base `d7c59d5` instead. The old immutable baseline is not regenerated.

Live tests must cover occult needs/abilities, book cart navigation/purchase, Gallery filters/descriptions, Manage Worlds transfers, scanner Enter/pie menus and CAS entry. No automated test should spend points or buy items without explicit action. Deferred Gallery changes and duplicate TimeControlsMain ownership remain separate follow-ups.

## Info-panel navigation follow-up

Needs, Simology and Aspirations now walk their fully instantiated controls directly, retaining native slider reveal. This avoids re-entering one-cell content wrappers or nested trait/goal grids. Empty temperament/curse slots use EA's IsEmpty getter; linked controller-highlight artwork is excluded from narration and focus. Code: TooltipManager.A11yFindScrollList, A11yKeyboardDecoration and A11yTextDecoration. Tests cover forward/backward traversal, later sections, independent pickers and decorative-control isolation. See changes/info-panel-navigation.md. In-game verification of this follow-up remains pending.
