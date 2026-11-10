# Requested screens and proactive navigation fixes

Game 1.129.39.1030; native UI SHA256 6807e477012eca956ee8ef744c00917d4f983547826a0af5c741391e94d0ac83.

| Screen | Change | Evidence |
| --- | --- | --- |
| Social Bunny | Keep readable posts/contacts and expose visible native message, remove, friend and reaction buttons with author/post context. | Native class inspection and production-method fixtures, including nested direct messages. |
| Running event goals | Events → selected event → Current event goals focuses its native goal HUD; stale event/zone scopes expire. | Native SituationDisplay identifiers and public panel method; identity, modal and cleanup fixtures. |
| Book-style text dialogs | Traverse native title/description row wrappers to their real input fields and existing footer. | Native TextInputCellView/InlineTextInputCellView and field/footer fixture. Native validation is retained. |
| Photography | Panels → Photography controls focuses an already open camera; native selected filters are announced. | Native SimCamera controls, selected-state and modal/closed-camera fixtures. |
| Wedding venue | Announce native selected state after activation. | Native LocationCellView.Selected and settled-readback checks. Selection failure itself is not established from static inspection. |
| Clubs, Gallery subscriptions, rental units, household cards | Expose visible native child actions hidden behind readable card wrappers. | Exact native class/field inspection and one fixture for each family. |

No game interactions were performed by these checks. In-game confirmation remains required for the reported book, photography and wedding scenarios. Unrelated screens retain the existing traversal. All shared TooltipManager definitions are rebuilt together for standard and UI Cheats packages.
