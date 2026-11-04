# UI port manifest

Base: Git d7c59d5. Game 1.129.39.1030. In-game panel verification pending.

- flash/TooltipManager_patched.as, around 3187, 3470, 6344, 6430, 6456 and 6830: occult rank/points; blocked-cart feedback; native ability/transfer controls; direct Needs/Simology/Aspirations traversal; skip empty occult slots and linked controller highlights.
- flash/extra-classes/CommodityContainer.as, around 160: trait-dependent need names and bounded percentages.
- flash/extra-classes/DialogMain.as, around 568: retain EA allowDuringLoading saving-dialog behavior.
- flash/prepare_uicheats_purchase.py and build_uicheats_compat.ps1: preserve UI Cheats' right-click ten-item quantities with narration.
- tools/ui_port_*, ui_bridge_inventory.py and regression fixtures: source/structure/handler verification, scanner picks, purchase controls and nested panel traversal.

Validation: 111 suites, 1,497 reported checks, passed with stable inputs. All 25 standard and 6 compatibility movies rebuilt; fidelity gates passed 62 and 19 targeted comparisons. Original non-code tags and class sets retained. 39 routing methods and the updated panel helpers/purchase guard match across all 29 shared-manager copies.

Rollback: restore the previous paired UI packages, or reverse CHANGES.patch against its recorded source state. SOURCE-MANIFEST.json records exact before/after hashes. Python scripts are unchanged.
