# Proactive native UI audit — 15 November 2026

Game baseline: 1.129.39.1030. Native movies were read from the installed UI.package and exported read-only. Twelve additional screen families were inventoried; relevant native fields, Draw visibility branches and event owners were compared with the production accessibility walker. No game interactions were performed.

| Native movie | Result |
| --- | --- |
| RestaurantMenu | Fix CourseCellView swallowing its nested dish grid; retain its heading as a separate read-only stop and FoodCellView swallowing its visible Remove action. Keep native order/edit modes and disabled checks. |
| SmallBusinessEmployeeManagement | Fix populated employee rows swallowing salary/fire controls. Read the public mcContent display container, not protected aliases; retain employee-name context for each action. |
| SmallBusinessConfigurator | Fix shared RuleCellView swallowing its native Remove action. Native hover still owns whether Remove is visible. |
| ClubDetails | Fix ClubRulesCellView swallowing its native Remove action. Keep the row's original add/edit action. |
| ClubRules | Same reviewed shared ClubRulesCellView behavior; no new movie override. |
| BusinessSettings | Fix inert ButtonWarningContainer/GenericTextButtonWarningContainer stopping traversal before the real inner button. Read exact native sibling labels for management dropdowns and employee outfits. |
| JewelryCrafting | Fix hidden mcLabels/mcContent branches contributing stale prompts or old material text to immediate row reads. Respect the native selected/empty/not-needed branches. |
| ClubRewards | Existing TextField visibility already suppresses hidden prices. Retain regression coverage; no change to reward purchasing or availability. |
| CollectionDisplay | Category progress already uses localized visible text; no demonstrated safe change in this pass. See follow-up below for icon-only data. |
| CareerSelector | Existing choice-description reader supplies the career row's native description. No new activation or selection change. |
| Calendar | Existing native Add proxies and informational schedule traversal cover the inspected action owners. No new change. |
| SimInfoRelationshipPanel | Inventoried native filter, track and relationship cells. No demonstrated scoped fix without a focused live case. |

## Deferred follow-up with concrete next steps

- Restaurant per-Sim Remove Food/Drink: SimGridCellView stores protected button aliases under public mcFood/mcDrink clips. Native indicator rollover reveals the corresponding button. A later isolated adapter should provide distinguishable indicator labels, preserve the order's locked state and verify synthetic hover/exit behavior. Do not force visibility or dispatch private removal methods.
- Collections: CollectionItemCellView uses a native tooltip data object rather than visible title text. Check whether fast keyboard traversal cancels that tooltip before reading it; if confirmed, add a class-specific read-only data label with found/missing state from the native tooltip fields.
- Relationship bars and reward eligibility: require native localized status/tooltip evidence before adding interpretations of icon/timeline state. Existing selection and purchase controls remain authoritative.

## Checks

Eighteen new source-executing fixtures exercise the four changed production methods and native click guards. Replaying them against the previous committed TooltipManager reproduces twelve failures; six unaffected/guard cases already pass. All eighteen pass with the candidate. Full regression and compiled-package outcomes are recorded in the candidate's VALIDATION and UI evidence files. In-game testing remains pending.
