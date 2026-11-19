#!/usr/bin/env python3
"""Static checks for the Order test datapack and KubeJS scripts. No game needed, runs in seconds.

    python tools/validate.py

Errors are things that break in game (a missing function, an unknown power, broken JSON).
Warnings are things that are probably a mistake (an unused function, a tag nothing ever adds).
Exit code 1 on any error.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
SCRIPTS = REPO / "kubejs" / "server_scripts"
RESOURCEPACK = REPO / "resourcepack"
PHOTON_FX_OPTION = re.compile(r"\b(?:open|loop|close|enter|memberLoop|exit)\s*:\s*'([a-z0-9_.-]+):([a-z0-9_./-]+)'")
NAMESPACE = "ordertest"
PACK_FORMAT = 15  # Minecraft 1.20.1
ORIGINS_NAMESPACES = ("origins", "apoli")
RESOURCE_TYPES = {f"{ns}:resource" for ns in ORIGINS_NAMESPACES}
LOAD_FUNCTION = f"{NAMESPACE}:load"

FUNCTION_REF = re.compile(r"\bfunction\s+(#?[a-z0-9_.-]+:[a-z0-9_./-]+)")
OBJECTIVE_ADD = re.compile(r"scoreboard objectives add\s+(\S+)")
OBJECTIVE_USES = (
    re.compile(r"scoreboard players (?:set|add|remove|reset|get|enable)\s+\S+\s+(\S+)"),
    re.compile(r"scoreboard players operation\s+\S+\s+(\S+)\s+\S+\s+\S+\s+(\S+)"),
    re.compile(r"\bif score\s+\S+\s+(\S+)"),
    re.compile(r"\bunless score\s+\S+\s+(\S+)"),
    re.compile(r"scores=\{([^}]*)\}"),
)
TAG_ADD = (re.compile(r"\btag\s+\S+\s+add\s+(\S+)"), re.compile(r"Tags:\[([^\]]*)\]"))
TAG_USE = re.compile(r"\btag=!?([A-Za-z0-9_.+-]+)")
# Tags the KubeJS engine puts on entities: string literals in scripts, plus the per-domain name tags.
JS_TAG_LITERAL = re.compile(r"'(ot_[a-z0-9_]+)'")
DYNAMIC_TAG_PREFIXES = ("ot_in_",)
JS_COMPONENT_DEF = re.compile(r"OrderTest\.component\(\s*'([a-z0-9_]+)'")
JS_COMPONENT_PAIR = re.compile(r"\[\s*'([a-z0-9_]+)'\s*,\s*\{")
JS_COMPONENT_LIST = re.compile(r"[cC]omponents\s*:\s*\[([^\]]*)\]")
# Rhino rejects this ("redeclaration of var") although node accepts it.
JS_CONST_IN_FOR = re.compile(r"\bfor\s*\([^)]*\)\s*\{[^}]*\bconst\b")
# Undefined in KubeJS's Rhino, so any maths using them silently becomes NaN.
JS_MATH_CONSTANT = re.compile(r"\bMath\.(PI|E|LN2|LN10|LOG2E|LOG10E|SQRT2|SQRT1_2)\b")
# A list element: a string right after '[' or ',', never an object value like target: 'others'.
JS_STRING = re.compile(r"[\[,]\s*'([a-z0-9_]+)'")
ENTITY_TYPE_TAG_REF = re.compile(r"type=!?#([a-z0-9_.-]+:[a-z0-9_./-]+)")


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: Path | str, msg: str):
        self.errors.append(f"{rel(where)}: {msg}")

    def warn(self, where: Path | str, msg: str):
        self.warnings.append(f"{rel(where)}: {msg}")


def rel(p: Path | str) -> str:
    return p.relative_to(REPO).as_posix() if isinstance(p, Path) else p


def resource_id(path: Path, kind_dir: Path, suffix: str) -> str:
    return f"{kind_dir.parent.name}:{path.relative_to(kind_dir).as_posix()[:-len(suffix)]}"


def load_json(path: Path, report: Report):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        report.error(path, f"invalid JSON: {e}")
        return None


def walk_strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from walk_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_strings(v)
    elif isinstance(node, str):
        yield node


def walk_dicts(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk_dicts(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_dicts(v)


def objective_names(line: str) -> list[str]:
    names = []
    for pattern in OBJECTIVE_USES:
        for match in pattern.finditer(line):
            for group in match.groups():
                if "=" in group or "," in group:
                    names += [part.split("=")[0].strip() for part in group.split(",") if part.strip()]
                else:
                    names.append(group)
    return [n for n in names if n and not n.startswith("#")]


def main() -> int:
    report = Report()
    check_pack_meta(report)

    functions = {resource_id(p, d, ".mcfunction"): p
                 for d in DATA.glob("*/functions") for p in d.rglob("*.mcfunction")}
    function_tags = {f"#{d.parent.parent.name}:{p.relative_to(d).as_posix()[:-len('.json')]}": p
                     for d in DATA.glob("*/tags/functions") for p in d.rglob("*.json")}
    powers = {resource_id(p, d, ".json"): p for d in DATA.glob("*/powers") for p in d.rglob("*.json")}
    origins = {resource_id(p, d, ".json"): p for d in DATA.glob("*/origins") for p in d.rglob("*.json")}

    for path in DATA.rglob("*.json"):
        load_json(path, report)

    power_json = {pid: load_json(p, report) for pid, p in powers.items()}
    referenced_functions: dict[str, list[str]] = {}
    commands_by_source: list[tuple[Path, str]] = []

    for tag_id, path in function_tags.items():
        tag = load_json(path, report) or {}
        for value in tag.get("values", []):
            ref = value if isinstance(value, str) else value.get("id", "")
            referenced_functions.setdefault(ref, []).append(rel(path))

    for fid, path in functions.items():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("/"):
                report.error(f"{rel(path)}:{number}", "mcfunction lines must not start with '/'")
            commands_by_source.append((path, stripped))

    for pid, data in power_json.items():
        if data is None:
            continue
        check_power(pid, powers[pid], data, power_json, report)
        for text in walk_strings(data):
            if FUNCTION_REF.search(text):
                commands_by_source.append((powers[pid], text))

    for source, command in commands_by_source:
        for ref in FUNCTION_REF.findall(command):
            referenced_functions.setdefault(ref, []).append(rel(source))

    for ref, sources in referenced_functions.items():
        known = function_tags if ref.startswith("#") else functions
        if ref.split(":")[0].lstrip("#") in (NAMESPACE, "minecraft") and ref not in known:
            report.error(sources[0], f"references missing function {ref}")

    for fid, path in functions.items():
        if fid not in referenced_functions:
            report.warn(path, f"function {fid} is never called by a power, tag or another function")

    check_origins(origins, powers, report)
    check_layers(origins, report)
    check_scoreboards(functions, power_json, powers, commands_by_source, report)
    check_tags(commands_by_source, report)
    check_entity_type_tags(commands_by_source, report)
    scripts = check_scripts(report)

    report.errors = list(dict.fromkeys(report.errors))
    report.warnings = list(dict.fromkeys(report.warnings))
    for w in report.warnings:
        print(f"WARN   {w}")
    for e in report.errors:
        print(f"ERROR  {e}")
    print(f"\nvalidate: {len(report.errors)} error(s), {len(report.warnings)} warning(s); "
          f"{len(functions)} functions, {len(powers)} powers, {len(origins)} origin(s), {scripts} script(s)")
    return 1 if report.errors else 0


def check_pack_meta(report: Report):
    meta_path = REPO / "pack.mcmeta"
    if not meta_path.exists():
        report.error("pack.mcmeta", "missing")
        return
    meta = load_json(meta_path, report)
    if meta and meta.get("pack", {}).get("pack_format") != PACK_FORMAT:
        report.error(meta_path, f"pack_format should be {PACK_FORMAT} for Minecraft 1.20.1")


def check_power(pid: str, path: Path, data: dict, all_powers: dict, report: Report):
    power_type = data.get("type")
    if not isinstance(power_type, str) or ":" not in power_type:
        report.error(path, "power has no namespaced 'type'")
    elif power_type.split(":")[0] not in ORIGINS_NAMESPACES and power_type.split(":")[0] != NAMESPACE:
        report.warn(path, f"power type {power_type} is from an add-on; make sure the server has it")
    if not data.get("hidden") and (not data.get("name") or not data.get("description")):
        report.warn(path, "visible power has no name or description (set \"hidden\": true if intended)")
    for node in walk_dicts(data):
        ref = node.get("resource")
        if isinstance(ref, str):
            target = all_powers.get(ref)
            if ref not in all_powers:
                report.error(path, f"uses resource {ref} but no such power file exists")
            elif target and target.get("type") not in RESOURCE_TYPES:
                report.error(path, f"uses {ref} as a resource but its type is {target.get('type')}")
        if node.get("type") in {f"{ns}:{t}" for ns in ORIGINS_NAMESPACES for t in ("active_self", "active")}:
            if "key" not in node and node is data:
                report.warn(path, "active power has no 'key'; it binds to primary by default")


def check_origins(origins: dict, powers: dict, report: Report):
    used = set()
    for oid, path in origins.items():
        data = load_json(path, report) or {}
        for field in ("name", "description", "icon"):
            if field not in data:
                report.warn(path, f"origin has no '{field}'")
        for ref in data.get("powers", []):
            used.add(ref)
            if ref.split(":")[0] == NAMESPACE and ref not in powers:
                report.error(path, f"lists missing power {ref}")
    for pid, path in powers.items():
        if pid not in used:
            report.warn(path, f"power {pid} is not in any origin")


def check_layers(origins: dict, report: Report):
    for layer_path in DATA.glob("*/origin_layers/*.json"):
        layer = load_json(layer_path, report) or {}
        if layer_path.parent.parent.name == "origins" and layer.get("replace"):
            report.warn(layer_path, "replace: true on an Origins layer removes every other origin from it")
        for entry in layer.get("origins", []):
            refs = [entry] if isinstance(entry, str) else entry.get("origins", [])
            for ref in refs:
                if ref.split(":")[0] == NAMESPACE and ref not in origins:
                    report.error(layer_path, f"lists missing origin {ref}")


def check_scoreboards(functions: dict, power_json: dict, powers: dict, commands, report: Report):
    load_path = functions.get(LOAD_FUNCTION)
    created = set(OBJECTIVE_ADD.findall(load_path.read_text(encoding="utf-8"))) if load_path else set()
    for source, command in commands:
        for name in objective_names(command):
            if name not in created:
                report.error(source, f"scoreboard objective '{name}' is used but not created in {LOAD_FUNCTION}")
    for pid, data in power_json.items():
        for node in walk_dicts(data or {}):
            if str(node.get("type", "")).endswith(":scoreboard") and node.get("objective") not in created:
                report.error(powers[pid], f"scoreboard objective '{node.get('objective')}' is not created in {LOAD_FUNCTION}")


def check_tags(commands, report: Report):
    added, used = set(), {}
    for script in SCRIPTS.rglob("*.js"):
        added.update(JS_TAG_LITERAL.findall(script.read_text(encoding="utf-8")))
    for source, command in commands:
        for pattern in TAG_ADD:
            for match in pattern.findall(command):
                added.update(t.strip().strip('"') for t in match.split(","))
        for tag in TAG_USE.findall(command):
            used.setdefault(tag, rel(source))
    for tag, source in used.items():
        if tag not in added and not tag.startswith(DYNAMIC_TAG_PREFIXES):
            report.warn(source, f"entity tag '{tag}' is tested but never added")


def check_entity_type_tags(commands, report: Report):
    for source, command in commands:
        for ref in ENTITY_TYPE_TAG_REF.findall(command):
            namespace, path = ref.split(":")
            if namespace == NAMESPACE and not (DATA / namespace / "tags" / "entity_types" / f"{path}.json").exists():
                report.error(source, f"uses missing entity type tag #{ref}")


def check_scripts(report: Report) -> int:
    scripts = sorted(SCRIPTS.rglob("*.js"))
    node = shutil.which("node")
    if not node:
        report.warn("kubejs", "node is not installed, so script syntax was not checked")
    texts = {path: path.read_text(encoding="utf-8") for path in scripts}
    for path in scripts:
        if node:
            result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
            if result.returncode != 0:
                report.error(path, "JavaScript syntax error: " + result.stderr.strip().splitlines()[-1])
    generator = subprocess.run([sys.executable, "-I", str(REPO / "tools" / "photon" / "generate.py"), "--check"],
                               capture_output=True, text=True)
    if generator.returncode != 0:
        report.error("tools/photon/effects", "Photon effects fail their checks:\n" + generator.stdout.strip())
    defined = set()
    for text in texts.values():
        defined.update(JS_COMPONENT_DEF.findall(text))
    for path, text in texts.items():
        if JS_CONST_IN_FOR.search(text):
            report.error(path, "const inside a for loop body; Rhino rejects it, move the body into a function")
        for namespace, name in sorted(set(PHOTON_FX_OPTION.findall(text))):
            if not (RESOURCEPACK / "assets" / namespace / "fx" / f"{name}.fx").exists():
                report.warn(path, f"Photon effect {namespace}:{name} is not in resourcepack/assets/{namespace}/fx/ yet")
        for constant in sorted(set(JS_MATH_CONSTANT.findall(text))):
            report.error(path, f"Math.{constant} is undefined in KubeJS (results become NaN); use Math.acos(-1) for pi")
        used = set(JS_COMPONENT_PAIR.findall(text))
        for block in JS_COMPONENT_LIST.findall(text):
            used.update(JS_STRING.findall("[" + block))
        for component in sorted(used - defined):
            report.error(path, f"uses component '{component}' but no script defines it")
    return len(scripts)


if __name__ == "__main__":
    sys.exit(main())
