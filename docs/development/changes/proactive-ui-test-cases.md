# Native UI test cases — 15 November

Use a disposable/backed-up save with the relevant packs. These are manual cases; this audit did not interact with the game.

1. Restaurant menu: use Tab and arrows through courses and individual dishes. In menu editing, focus a dish then its visible Remove button. In ordering mode, confirm the existing native choice/confirmation flow still owns the action.
2. Clubs/rules: focus an editable activity or admission-rule row, then its Remove control. Read-only/non-editable rows must not gain a forced Remove action. Cancel or use a disposable rule when testing deletion.
3. Small-business employees: reach a populated employee row, then salary and fire. Each child action should include that employee's name. Opening salary should show the native picker; fire should retain the native confirmation. Cancel both when only checking access.
4. Restaurant/vet settings: focus menu/warning button wrappers and verify the working inner control is selected. Management dropdowns and employee outfits should include their adjacent localized label as well as their current value/tooltip.
5. Jewelry: compare an empty material slot, selected metal/crystal/design and a native not-needed crystal state. Selected rows should read the current name/price without the hidden empty-slot instructions; empty rows should not read the previous material.
6. Neighbor checks: existing Game Options, scanner Enter, ordinary purchase picker, Social Bunny actions, apartment/scenario navigation and occult panel traversal should keep their previous behavior.

Compiler gates and display-tree fixtures cannot establish live selection, focus timing or tooltip timing. Record the UI package hashes and a short focused log with any failed case.

## Unbound right-click action

No shortcut is assigned yet. A developer can request A11yRightClick through tyjokr_a11y_keys._send after normal UI focus has settled. On a need bar, expect the native Set Motive dialog; on the currency control, expect the native money dialog. Cancel without entering values for a read-only smoke check. Verify one dialog/action only and compare right-click|sent coordinates in a short diagnostic log. Native milestone/buff/goal right-click actions may act immediately, so test those only in a disposable save. Verify missing UI Cheats, hidden/stale controls, text entry and pending navigation refuse. This action targets UI controls, not scanner/world objects.
