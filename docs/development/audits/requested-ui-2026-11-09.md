# Requested UI audit — 2026-11-09

Read-only audit of game 1.129.39.1030. Native UI.package SHA256: 6807e477012eca956ee8ef744c00917d4f983547826a0af5c741391e94d0ac83. Extracted current SocialMedia, SituationCreation, SituationDisplay, ChallengeEventDisplay, Dialog, Book, SimCamera and CameraControl. No fixes to these screens applied.

## Social Bunny — confirmed traversal gap

Native SocialMediaFriendCellView contains btnSendMessage and btnRemoveFriend; feed rows contain btnReaction and conditionally btnAddFriend. Their native handlers use PushButtonEvent.CLICK. Current A11yCollectFocusables stops at these CellView wrappers because A11yCompositeRow does not recognize them. An offline fixture executing production traversal reproduces the inaccessible child actions for friend, feed and message rows. Keep one readable post/contact stop, then expose its visible native child actions with localized tooltips and the associated Sim/post context. Do not assign a guessed default action to the wrapper.

Evidence: build/requested-ui-audit/SocialMedia; build/audit_requested_ui_navigation.js. Source-derived fixture, not in-game confirmation.

## Event goals — native information available; menu coverage missing

SituationDisplay's SituationGoalCellView/GoalIconContainer contain localized goal names, progression text and native goal tooltips. Current accessibility Events menu in tyjokr_a11y_hub.py offers ending/leaving actions but no goal reader. A read-only Goals entry for the selected current event is a concrete extension; it must follow native active goal data and discard stale goals at event/zone changes. Automatic goal announcements need separate deduplication and opt-in consideration.

## Wedding venue selection — cause not yet established

Native LocationCellView is already a Button with venue/lot/neighborhood text. LocationListView uses selectable-group SELECTION_CHANGED, native expanded-world lists and eligibility filtering. Existing mod has role-slot and wizard navigation support. Static inspection does not prove venue selection itself is broken. Check expanded-list traversal, native selection acknowledgement and disabled/rejection state before proposing an activation change. Never bypass venue eligibility or trigger event creation while auditing.

## Book title/description confirmation — cause not yet established

Native text-input headers synchronize their model on Event.CHANGE and emit VALID/INVALID after ValidateValue. The mod deliberately passes typing and Enter to the native editor while editing; Enter may insert a newline. The current close-button exclusion targets btnClose, not confirmation. Cannot establish from static code whether the reported failure is an unreachable response, a disabled response or text validation. A focused read-only UI capture should record the actual text-input header, response controls and validation state; do not force-enable or auto-submit the dialog.

## Photography — native shutter exists; missing labels not yet proven

SimCameraMain.btnCamera has TAKE_PICTURE tooltip and OnCameraClicked routes through PhotographyTakePhoto. Therefore missing shutter access is not an absent native API. CameraFilterCellView receives its localized tooltipLocKey outside console-input mode and intentionally disables the selected filter. Current generic checkbox-state logic does not identify these filters as selected. Check modal/scope ownership, native input mode, selected-filter narration and viewport pruning before changing focus. Preserve filters_disabled, camera-quality, photo-count and native shutter validation. No photos taken during audit.

## Next validation

Use the existing read-only UI inspector on the affected screen when a reproducible session is available. Keep uncertain book, venue and shutter causes scoped separately. Social Bunny child-action traversal is the strongest offline-confirmed repair candidate.
