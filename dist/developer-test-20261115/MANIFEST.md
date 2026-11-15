# Developer manifest

Base: upstream adb868c. CHANGES.patch is cumulative and reverse-checked; changed-source contains only differing sources. SOURCE-MANIFEST.json records hashes/deletions.

15 November UI changes: flash/TooltipManager_patched.as, A11yCollectFocusables around 5205 (native child actions), A11yCompositeRow 6876 (restaurant courses/warning wrappers), A11yOptionsRowLabel 6471 (business labels/employee context), A11yTextDecoration 6760 (jewelry branches). Tests: tools/test_proactive_ui_native.js. Native findings/deferred cases: changed-source/docs/development/audits/proactive-ui-20261115.md.

Earlier work is grouped in changed-source/contrib-reference/docs/DEVELOPER-MANIFEST.md. TooltipManager_patched.as adds A11yRightClickOwner around 8132, A11yTryRightClick 8196 and A11yMsgRightClick 8246; its existing stage hook registers the message. keys.py _send around 662 adds A11yRightClick to the existing activation-epoch fence. No shortcut is assigned. The other 68 compiled entries are byte-identical to the preceding script. Both UI packages are rebuilt together. This candidate has not been installed into the game.
