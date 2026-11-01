"""Runtime extension of TS4 Access' existing config and accessible settings menu."""

import configparser


SCOPE_KEY = "contrib_scanner_scope"
FLAG_KEYS = (
    "surface_layer_focus",
    "chair_alignment_hints",
    "experimental_bare_ground",
    "experimental_water",
    "experimental_ceiling",
    "experimental_fence",
)
SCOPE_CHOICES = (
    "6 meters", "12 meters", "24 meters", "40 meters",
    "whole lot", "this floor", "this room",
)
_original_render = None
_original_apply = None


def _on(value):
    return "on" if bool(value) else "off"


def _render(stored):
    import tyjokr_a11y_settings as settings
    base = _original_render(stored).rstrip() + "\n\n"
    get = lambda key: stored[key] if key in stored else settings.DEFAULTS.get(key)
    return base + (
        "[contribution]\n"
        "# Scanner scope restored at game start\n"
        "scanner scope = {}\n"
        "# Experimental Build-grid placement; every placement still requires the game's exact validator\n"
        "surface layer focus = {}\n"
        "chair alignment hints = {}\n"
        "experimental bare ground = {}\n"
        "experimental water = {}\n"
        "experimental ceiling = {}\n"
        "experimental fence = {}\n"
    ).format(
        get(SCOPE_KEY),
        _on(get("surface_layer_focus")),
        _on(get("chair_alignment_hints")),
        _on(get("experimental_bare_ground")),
        _on(get("experimental_water")),
        _on(get("experimental_ceiling")),
        _on(get("experimental_fence")),
    )


def _load_contribution_values(settings):
    parser = configparser.ConfigParser(
        inline_comment_prefixes=(";", "#"), interpolation=None, strict=False,
        empty_lines_in_values=False,
    )
    try:
        with open(settings.PATH, "r", encoding="utf-8") as handle:
            parser.read_file(handle)
    except Exception:
        return
    if not parser.has_section("contribution"):
        return
    scope = parser.get("contribution", "scanner scope", fallback="").strip().lower()
    if scope in SCOPE_CHOICES:
        settings._stored[SCOPE_KEY] = scope
    for option, key in (
        ("surface layer focus", "surface_layer_focus"),
        ("chair alignment hints", "chair_alignment_hints"),
        ("experimental bare ground", "experimental_bare_ground"),
        ("experimental water", "experimental_water"),
        ("experimental ceiling", "experimental_ceiling"),
        ("experimental fence", "experimental_fence"),
    ):
        raw = parser.get("contribution", option, fallback="").strip().lower()
        if raw in settings._TRUE_WORDS:
            settings._stored[key] = True
        elif raw in settings._FALSE_WORDS:
            settings._stored[key] = False


def _menu_apply(row, value):
    result = _original_apply(row, value)
    if row.key == SCOPE_KEY:
        try:
            import tyjokr_a11y_contrib as contrib
            contrib.set_scope(value, refresh=True)
        except Exception:
            pass
    return result


def _install_menu():
    global _original_apply
    try:
        import tyjokr_a11y_menu as menu
        if getattr(menu, "_contribution_settings_installed", False):
            return
        insert_at = next((i for i, row in enumerate(menu.ROWS) if row.key == "reload"), len(menu.ROWS))
        rows = [
            menu.Row(SCOPE_KEY, "choice", "scanner scope", choices=SCOPE_CHOICES,
                     help="saved scope for Control comma and Control period"),
            menu.Row("surface_layer_focus", "bool", "surface-layer object focus",
                     help="number 1 focuses the selected layer; number 4 names nearby object layers"),
            menu.Row("chair_alignment_hints", "bool", "chair-to-table orientation hints",
                     help="for dining and desk chairs, names the nearest compatible table and facing relation"),
            menu.Row("experimental_bare_ground", "bool", "experimental bare-ground placement",
                     help="requires natural ground and exact game validation"),
            menu.Row("experimental_water", "bool", "experimental water placement",
                     help="requires detected water and exact game validation"),
            menu.Row("experimental_ceiling", "bool", "experimental ceiling placement",
                     help="uses a sampled ceiling anchor and exact game validation"),
            menu.Row("experimental_fence", "bool", "experimental fence placement",
                     help="uses the selected blocked edge and exact game validation"),
        ]
        menu.ROWS[insert_at:insert_at] = rows
        menu._SETTING_ROWS = [row for row in menu.ROWS if row.kind != "action"]
        _original_apply = menu._apply
        menu._apply = _menu_apply
        menu._contribution_settings_installed = True
    except Exception:
        pass


def install():
    global _original_render
    import tyjokr_a11y_settings as settings
    if getattr(settings, "_contribution_schema_installed", False):
        return
    settings.DEFAULTS.update({
        SCOPE_KEY: "40 meters",
        "surface_layer_focus": True,
        "chair_alignment_hints": True,
        "experimental_bare_ground": True,
        "experimental_water": True,
        "experimental_ceiling": True,
        "experimental_fence": True,
    })
    settings._FILE_MAP.update({
        ("contribution", "scanner scope"): SCOPE_KEY,
        ("contribution", "surface layer focus"): "surface_layer_focus",
        ("contribution", "chair alignment hints"): "chair_alignment_hints",
        ("contribution", "experimental bare ground"): "experimental_bare_ground",
        ("contribution", "experimental water"): "experimental_water",
        ("contribution", "experimental ceiling"): "experimental_ceiling",
        ("contribution", "experimental fence"): "experimental_fence",
    })
    settings._BOOL_KEYS = tuple(settings._BOOL_KEYS) + tuple(
        key for key in FLAG_KEYS if key not in settings._BOOL_KEYS
    )
    _original_render = settings._render
    settings._render = _render
    _load_contribution_values(settings)
    settings._contribution_schema_installed = True
    _install_menu()


def value(key):
    import tyjokr_a11y_settings as settings
    return settings.get(key, settings.DEFAULTS.get(key))


install()
