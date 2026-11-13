"""Refresh only contribution bytecode in an existing, player-tested package."""
import pathlib
import py_compile
import shutil
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOWNLOADS = pathlib.Path(r'C:\Users\mirad\OneDrive\Downloads')
CLEAN = DOWNLOADS / 's4access update contrib'
BASE = CLEAN / 'TS4_Access' / 'TS4_Access.ts4script'
OUT = ROOT / 'dist' / 'contribution-test' / 'TS4_Access.ts4script'

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'contrib-reference' / 'modules').glob('*.py'))
    with tempfile.TemporaryDirectory(prefix='s4access-compile-') as temp:
        replacements = {}
        for source in sources:
            compiled = pathlib.Path(temp) / (source.stem + '.pyc')
            py_compile.compile(str(source), cfile=str(compiled), dfile=source.name, doraise=True)
            replacements[compiled.name] = compiled.read_bytes()
        with zipfile.ZipFile(str(BASE)) as old:
            original = {name: old.read(name) for name in old.namelist()}
            assert set(replacements).issubset(original), 'Contribution entries missing from baseline'
            with zipfile.ZipFile(str(OUT), 'w') as new:
                for info in old.infolist():
                    new.writestr(info, replacements.get(info.filename, original[info.filename]))
        with zipfile.ZipFile(str(OUT)) as check:
            assert check.testzip() is None
            assert set(check.namelist()) == set(original)
            for name, data in original.items():
                assert check.read(name) == replacements.get(name, data)
    backup = CLEAN.parent / 's4access-before-audit-2026-11-01.ts4script'
    if not backup.exists():
        shutil.copy2(str(BASE), str(backup))
    for source in sources:
        shutil.copy2(str(source), str(CLEAN / 'developer-source' / source.name))
    for doc in (ROOT / 'contrib-reference' / 'docs').glob('*.md'):
        shutil.copy2(str(doc), str(CLEAN / doc.name))
    shutil.copy2(str(OUT), str(BASE))
    shutil.copy2(str(OUT), str(DOWNLOADS / 'S4Access-Contribution-Test.ts4script'))
    with zipfile.ZipFile(str(DOWNLOADS / 's4access update contrib.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(CLEAN.rglob('*')):
            if path.is_file():
                archive.write(str(path), path.relative_to(CLEAN).as_posix())
    print('PASS: eleven modules compiled; other archive entries unchanged; Downloads synchronized')

if __name__ == '__main__':
    main()
