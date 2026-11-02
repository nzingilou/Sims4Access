# Changelog

- Room-construction overview retries now widen the camera distance around fixed room bounds; blocked screen points stop drawing and log framing details.

- Added saved scanner scopes: 6/12/24/40 metres, whole lot, current floor, and current room. Sims remain unfiltered in metre modes.
- Added reversible Build-grid furniture move/sell support, clearer wall/room-side announcements, named-room integration, and validated wall height/anchoring.
- Added independently configurable, game-validated bare-ground, water, ceiling, fence, and surface-layer placement helpers.
- Added room/build/lot descriptions, rectangular roof and chimney assistance, stacked-house planning, lot/building naming, and detached-structure planning.
- Added optional dining-chair and desk-chair orientation hints. Existing fit speech is retained; the hint names the nearest compatible table/desk within two tiles and says toward, away, or side-on. It does not alter placement.
- Withdrew the experimental UI-package rebase after in-game testing showed scanner Enter requests no longer opened pie menus. Distribution retains the update's original UI package.
- Adapted surface-layer focus and grid move/sell targeting to the update's current APIs. Repeated `1` presses now include attached contents (for example, a television on its stand), so the focused child can be sold separately; attached-object movement remains safely refused.
- The additive Build Helper wrapper now hides the original `Put a roof on my house` and `Describe the lot` rows because the accessible roof builder and lot/building description supersede them. Original functions are unchanged and return when the wrapper is removed.
