# Proactive native UI navigation

- Restaurant course wrappers retain a read-only heading and expose the existing dish grid; food, club-rule and shared-rule rows retain their summary/action and expose native visible Remove controls.
- Small-business employee rows expose salary/fire through public mcContent, with employee-name context. Business warning wrappers expose their real inner button. Management/outfit controls read their exact native sibling labels.
- Jewelry material rows omit explicitly hidden selected/empty/not-needed branches from immediate row narration.

Code: flash/TooltipManager_patched.as, A11yCollectFocusables (around 5205), A11yCompositeRow (6876), A11yOptionsRowLabel (6471) and A11yTextDecoration (6760). No Python command, keyboard binding, native event handler or movie list changes. Eighteen source-executing fixtures in tools/test_proactive_ui_native.js include visibility, identity, disabled actions and unrelated-control isolation. Native findings and deferred cases: docs/development/audits/proactive-ui-20261115.md.
