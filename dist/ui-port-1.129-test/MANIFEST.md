# UI port manifest

Base: Git d7c59d5. Game 1.129.39.1030. Test candidate; in-game verification pending.

- flash/TooltipManager_patched.as, around 3187 and 6427: occult rank/points stops; traverse ability-rank and transfer-neighborhood containers to their native controls.
- flash/extra-classes/CommodityContainer.as, around 160: trait-dependent need names and bounded percentages.
- flash/extra-classes/DialogMain.as, around 568: retain EA allowDuringLoading saving-dialog behavior.
- flash/prepare_uicheats_purchase.py and build_uicheats_compat.ps1: preserve right-click ten-item quantity changes with narration. gate_compat_pcode.py supports isolated reviewed inputs.
- tools/ui_port_* and ui_bridge_inventory.py: extraction, source, structure and compiled-handler audit helpers. Scanner-pick, occult narration and traversal fixtures added; four existing test summaries made countable.

Validation: 25 standard plus 6 compatibility movies; fidelity gates passed 62 plus 19 targeted comparisons; exact original non-code tags and class sets retained. 39 routing methods match across 29 compiled copies. 1,482 checks across 110 suites passed with stable inputs (includes repeated imported checks).

Source rollback: CHANGES.patch is anchored to the Git base above and passed a reverse-application check. SOURCE-MANIFEST.json records original and changed source hashes. The detailed remaining audit targets are in docs/development/UI-PORT-1.129.md.
