#!/usr/bin/env python3
"""Local Forge 1.20.1 + Origins + KubeJS test server for the Order test pack.

Same Forge, Origins and Java 17 as the "Just Origins" CurseForge instance, plus KubeJS. Mod versions come from
gradle.properties (`gradlew installServerMods`), so the server and `gradlew runClient` always match.

    python tools/testserver.py setup          # once: install Forge server, mods, config
    python tools/testserver.py start          # start in the background and wait for "Done"
    python tools/testserver.py sync           # copy the datapack and KubeJS scripts in, /reload, show errors
    python tools/testserver.py rcon <cmd...>  # run a command, print the reply
    python tools/testserver.py test           # validate, sync, reload, run tests/*.mctest, report
    python tools/testserver.py stop
    python tools/testserver.py deploy <save>  # copy the datapack into a Just Origins singleplayer save
    python tools/testserver.py zip            # build dist/ordertest.zip and dist/ordertest-kubejs.zip
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import struct
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack_sources  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
PACK_ID = "ordertest"
SCRIPTS_DIR = REPO / "kubejs" / "server_scripts"
SERVER_DIR = REPO / ".testserver"
WORLD_DIR = SERVER_DIR / "world"
PACK_DEST = WORLD_DIR / "datapacks" / PACK_ID
SERVER_SCRIPTS_DEST = SERVER_DIR / "kubejs" / "server_scripts"
STATE_FILE = SERVER_DIR / "devserver.json"
LOG_FILE = SERVER_DIR / "logs" / "latest.log"
KUBEJS_LOG_FILE = SERVER_DIR / "logs" / "kubejs" / "server.log"
CLIENT_DIR = REPO / "run"
CLIENT_SAVES_DIR = CLIENT_DIR / "saves"
CLIENT_SCRIPTS_LINK = CLIENT_DIR / "kubejs" / "server_scripts"
RESOURCEPACK_DIR = REPO / "resourcepack"
CLIENT_RESOURCEPACK_LINK = CLIENT_DIR / "resourcepacks" / PACK_ID
# The Photon editor exports into <game>/ldlib/assets/...; this link puts exports straight into the pack.
CLIENT_EDITOR_EXPORT_LINK = CLIENT_DIR / "ldlib" / "assets" / PACK_ID
CLIENT_OPTIONS = CLIENT_DIR / "options.txt"
DEV_CLIENT_SCRIPT = REPO / "tools" / "dev_client" / "ordertest_dev_client.js"
CLIENT_DEV_SCRIPT_DEST = CLIENT_DIR / "kubejs" / "client_scripts" / DEV_CLIENT_SCRIPT.name
CLIENT_DEV_CONFIG = CLIENT_DIR / "kubejs" / "config" / "ordertest_dev.json"
DEFAULT_JOIN_TIMEOUT_S = 180
RESOURCE_PACKS_OPTION = "resourcePacks:"
CLIENT_PACK_ENTRY = f"file/{PACK_ID}"
CLIENT_WORLD_NAME = "ordertest_test"
JS_POWER_PATTERN = re.compile(r"OrderTest\.power\(\s*'([a-z0-9_.-]+:[a-z0-9_./-]+)'")
# NBT TAG_Byte (type 1) named "allowCommands" (length 13); the value byte follows.
ALLOW_COMMANDS_TAG = b"\x01\x00\x0dallowCommands"
DIST_DIR = REPO / "dist"
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)

MC_VERSION = "1.20.1"
FORGE_VERSION = "47.4.28"
FORGE_INSTALLER_URL = (
    f"https://maven.minecraftforge.net/net/minecraftforge/forge/{MC_VERSION}-{FORGE_VERSION}/"
    f"forge-{MC_VERSION}-{FORGE_VERSION}-installer.jar"
)
# The Forge maven refuses Python's default "Python-urllib" agent with 403.
DOWNLOAD_USER_AGENT = "ordertest-testserver/1.0"
CURSEFORGE = Path.home() / "curseforge" / "minecraft"
INSTANCE_DIR = Path(os.environ.get("OT_INSTANCE", CURSEFORGE / "Instances" / "Just Origins"))
GRADLE = REPO / ("gradlew.bat" if os.name == "nt" else "gradlew")
JAVA17_CANDIDATES = (
    CURSEFORGE / "Install" / "runtime" / "java-runtime-gamma" / "windows-x64" / "java-runtime-gamma" / "bin" / "java.exe",
)

RCON_HOST = "127.0.0.1"
RCON_PORT = 25576
SERVER_PORT = 25565
SERVER_MEMORY = "3G"
START_TIMEOUT_S = 240
STOP_TIMEOUT_S = 60
DONE_PATTERN = re.compile(r"Done \([\d.,]+s\)!")
LOAD_ERROR_PATTERNS = (
    re.compile(r"Failed to load function", re.I),
    re.compile(r"There was a problem reading power", re.I),
    re.compile(r"Couldn't load tag .* missing following references", re.I),
    re.compile(r"Error loading (power|origin)", re.I),
    re.compile(r"(error|exception|failed|couldn't|could not|unknown).*" + PACK_ID, re.I),
    re.compile(PACK_ID + r".*(error|exception|failed|couldn't|could not|unknown)", re.I),
)
KUBEJS_ERROR_PATTERN = re.compile(r"\[(ERR|ERROR|WARN)\s*\]|Error in |error loading|\[ordertest\]", re.I)
RELOAD_SETTLE_S = 3


def java_executable() -> str:
    override = os.environ.get("OT_JAVA")
    if override:
        return override
    for candidate in JAVA17_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return "java"


# ---------- RCON ----------

class Rcon:
    LOGIN, COMMAND = 3, 2

    def __init__(self, password: str, timeout: float = 10.0):
        self.sock = socket.create_connection((RCON_HOST, RCON_PORT), timeout=timeout)
        self.next_id = 1
        if self._request(self.LOGIN, password)[0] == -1:
            raise RuntimeError("RCON login refused")

    def _request(self, kind: int, body: str) -> tuple[int, str]:
        request_id = self.next_id
        self.next_id += 1
        payload = struct.pack("<ii", request_id, kind) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        size = struct.unpack("<i", self._read(4))[0]
        reply_id, _ = struct.unpack("<ii", self._read(8))
        text = self._read(size - 8)[:-2].decode("utf-8", "replace")
        return reply_id, text

    def _read(self, n: int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("RCON connection closed")
            data += chunk
        return data

    def command(self, cmd: str) -> str:
        return strip_formatting(self._request(self.COMMAND, cmd)[1])

    def close(self):
        self.sock.close()


def strip_formatting(text: str) -> str:
    return re.sub("§.", "", text)


def rcon_password() -> str:
    for line in (SERVER_DIR / "server.properties").read_text(encoding="utf-8").splitlines():
        if line.startswith("rcon.password="):
            return line.split("=", 1)[1]
    raise RuntimeError("rcon.password missing from server.properties; run setup")


def connect(retries: int = 1) -> Rcon:
    if not (SERVER_DIR / "server.properties").exists():
        raise SystemExit("test server is not set up; run: python tools/testserver.py setup")
    last = None
    for _ in range(retries):
        try:
            return Rcon(rcon_password())
        except OSError as error:
            last = error
            time.sleep(1)
    raise RuntimeError(f"cannot reach the test server over RCON ({last}); is it running?")


def is_running() -> bool:
    if not (SERVER_DIR / "server.properties").exists():
        return False
    try:
        connect().close()
        return True
    except (RuntimeError, OSError):
        return False


# ---------- setup ----------

def cmd_setup(args) -> int:
    SERVER_DIR.mkdir(exist_ok=True)
    install_forge(force=args.force)
    install_mods()
    write_config()
    sync_pack()
    print(f"Test server ready in {SERVER_DIR}")
    return 0


def install_forge(force: bool):
    if (SERVER_DIR / "run.bat").exists() and not force:
        print("Forge server already installed")
        return
    installer = SERVER_DIR / f"forge-{MC_VERSION}-{FORGE_VERSION}-installer.jar"
    if not installer.exists():
        print(f"Downloading {FORGE_INSTALLER_URL}")
        request = urllib.request.Request(FORGE_INSTALLER_URL, headers={"User-Agent": DOWNLOAD_USER_AGENT})
        with urllib.request.urlopen(request) as response, open(installer, "wb") as out:
            shutil.copyfileobj(response, out)
    print("Installing Forge server (downloads vanilla server and libraries)...")
    subprocess.run([java_executable(), "-jar", installer.name, "--installServer"], cwd=SERVER_DIR, check=True,
                   stdout=subprocess.DEVNULL)
    installer.unlink()
    (SERVER_DIR / f"{installer.name}.log").unlink(missing_ok=True)


def install_mods():
    print("Installing server mods with Gradle (versions from gradle.properties)...")
    subprocess.run([str(GRADLE), "installServerMods", "--console=plain", "-q"], cwd=REPO, check=True)
    for jar in sorted((SERVER_DIR / "mods").glob("*.jar")):
        print(f"  mod: {jar.name}")


def write_config():
    (SERVER_DIR / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    (SERVER_DIR / "user_jvm_args.txt").write_text(f"-Xmx{SERVER_MEMORY}\n", encoding="utf-8")
    props_file = SERVER_DIR / "server.properties"
    existing = {}
    if props_file.exists():
        for line in props_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                existing[key] = value
    wanted = {
        "online-mode": "false",
        "server-ip": "127.0.0.1",
        "server-port": str(SERVER_PORT),
        "enable-rcon": "true",
        "rcon.port": str(RCON_PORT),
        "rcon.password": existing.get("rcon.password") or secrets.token_hex(12),
        "broadcast-rcon-to-ops": "false",
        "level-name": WORLD_DIR.name,
        "level-type": "minecraft\\:flat",
        "generate-structures": "false",
        "spawn-protection": "0",
        "gamemode": "creative",
        "difficulty": "normal",
        "spawn-monsters": "false",
        "view-distance": "6",
        "simulation-distance": "6",
        "motd": "Order test server",
    }
    existing.update(wanted)
    props_file.write_text("".join(f"{k}={v}\n" for k, v in existing.items()), encoding="utf-8")


def copy_files(files: dict[str, Path], dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    for rel, src in files.items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / rel)


def copy_pack(dest: Path):
    """The shipped datapack: data/ plus every origins/<name>/data/, merged."""
    copy_files(pack_sources.datapack_files(), dest)


def sync_pack():
    copy_pack(PACK_DEST)
    copy_files(pack_sources.script_files(), SERVER_SCRIPTS_DEST)


# ---------- lifecycle ----------

def cmd_start(args) -> int:
    if is_running():
        print("Test server is already running")
        return 0
    if not (SERVER_DIR / "run.bat").exists():
        raise SystemExit("not set up; run: python tools/testserver.py setup")
    sync_pack()
    args_name = "win_args.txt" if os.name == "nt" else "unix_args.txt"
    args_file = next((SERVER_DIR / "libraries" / "net" / "minecraftforge" / "forge").glob("*/" + args_name))
    command = [java_executable(), "@user_jvm_args.txt", f"@{args_file.relative_to(SERVER_DIR)}", "nogui"]
    console = open(SERVER_DIR / "console.log", "w", encoding="utf-8")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if os.name == "nt" else 0
    process = subprocess.Popen(command, cwd=SERVER_DIR, stdin=subprocess.DEVNULL, stdout=console,
                               stderr=subprocess.STDOUT, creationflags=flags)
    STATE_FILE.write_text(json.dumps({"pid": process.pid}), encoding="utf-8")
    print(f"Starting test server (pid {process.pid}), waiting up to {START_TIMEOUT_S}s...")
    deadline = time.time() + START_TIMEOUT_S
    while time.time() < deadline:
        if process.poll() is not None:
            print(f"Server exited with code {process.returncode} before it was ready; see {SERVER_DIR / 'console.log'}")
            return 1
        if LOG_FILE.exists() and DONE_PATTERN.search(LOG_FILE.read_text(encoding="utf-8", errors="replace")):
            if is_running():
                print("Test server is up (localhost)")
                prepare_world()
                return 0
        time.sleep(2)
    print("Server never reached Done; killing it so it does not hold the port")
    kill_server(process.pid)
    return 1


def prepare_world():
    rcon = connect(retries=5)
    for rule in ("doDaylightCycle false", "doWeatherCycle false", "doMobSpawning false",
                 "commandBlockOutput false", "sendCommandFeedback true"):
        rcon.command(f"gamerule {rule}")
    rcon.command("time set noon")
    rcon.command("weather clear")
    rcon.close()


def cmd_stop(args) -> int:
    if not is_running():
        print("Test server is not running")
        STATE_FILE.unlink(missing_ok=True)
        return 0
    connect().command("stop")
    pid = json.loads(STATE_FILE.read_text())["pid"] if STATE_FILE.exists() else None
    deadline = time.time() + STOP_TIMEOUT_S
    while time.time() < deadline and is_running():
        time.sleep(1)
    time.sleep(2)
    if pid and process_alive(pid):
        kill_server(pid)
    STATE_FILE.unlink(missing_ok=True)
    print("Test server stopped")
    return 0


def process_alive(pid: int) -> bool:
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def kill_server(pid: int):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
    else:
        os.kill(pid, 9)


# ---------- reload and log checks ----------

def log_size(path: Path = LOG_FILE) -> int:
    return path.stat().st_size if path.exists() else 0


def log_since(offset: int, path: Path = LOG_FILE) -> str:
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        # KubeJS rewrites its log on reload, so a shorter file means start from the top.
        f.seek(offset if offset <= path.stat().st_size else 0)
        return f.read().decode("utf-8", "replace")


def kubejs_errors(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if KUBEJS_ERROR_PATTERN.search(line)]


def load_errors(text: str) -> list[str]:
    errors = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if any(p.search(line) for p in LOAD_ERROR_PATTERNS):
            errors.append("\n    ".join(lines[i:i + 3]))
    return errors


def reload_and_check(rcon: Rcon) -> list[str]:
    sync_pack()
    offset = log_size()
    kubejs_offset = log_size(KUBEJS_LOG_FILE)
    rcon.command("reload")
    time.sleep(RELOAD_SETTLE_S)
    return load_errors(log_since(offset)) + kubejs_errors(log_since(kubejs_offset, KUBEJS_LOG_FILE))


def cmd_sync(args) -> int:
    rcon = connect()
    errors = reload_and_check(rcon)
    rcon.close()
    report_load_errors(errors)
    return 1 if errors else 0


def report_load_errors(errors: list[str]):
    if errors:
        print(f"FAIL  {len(errors)} load error(s) after /reload:")
        for e in errors:
            print("    " + e)
    else:
        print("PASS  pack reloaded with no load errors")


def cmd_rcon(args) -> int:
    rcon = connect()
    print(rcon.command(" ".join(args.command)))
    rcon.close()
    return 0


# ---------- tests ----------

def pack_powers() -> list[str]:
    """Powers from datapack JSON plus powers the KubeJS scripts inject with OrderTest.power."""
    powers = []
    for root in pack_sources.data_roots():
        for namespace in root.iterdir():
            powers_dir = namespace / "powers"
            for path in powers_dir.rglob("*.json"):
                powers.append(f"{namespace.name}:{path.relative_to(powers_dir).as_posix()[:-len('.json')]}")
    for script in pack_sources.script_files().values():
        powers += JS_POWER_PATTERN.findall(script.read_text(encoding="utf-8"))
    return sorted(set(powers))


def run_builtin_checks(rcon: Rcon) -> list[tuple[str, bool, str]]:
    results = []
    enabled = rcon.command("datapack list enabled")
    results.append(("datapack enabled", f"file/{PACK_ID}" in enabled, enabled))
    components = rcon.command("domain components")
    results.append(("KubeJS scripts loaded (/domain components)", "Components:" in components, components))
    rcon.command("kill @e[tag=ot_probe]")
    rcon.command('summon minecraft:armor_stand 0 -60 0 {Tags:["ot_probe"],NoGravity:1b,Invisible:1b}')
    for power in pack_powers():
        reply = rcon.command(f"power grant @e[tag=ot_probe,limit=1] {power}")
        results.append((f"power loads: {power}", is_grant_ok(reply), reply))
    rcon.command("kill @e[tag=ot_probe]")
    return results


def is_grant_ok(reply: str) -> bool:
    return bool(re.search(r"(granted|gave|added|success)", reply, re.I)) and not re.search(
        r"(unknown|not found|invalid|error|failed)", reply, re.I)


def run_test_file(rcon: Rcon, path: Path) -> list[tuple[str, bool, str]]:
    """A .mctest line is a command, optionally `=> regex` the reply must match, or `wait <ticks>`."""
    results = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("wait "):
            time.sleep(int(line.split()[1]) / 20)
            continue
        command, _, expected = (part.strip() for part in line.partition("=>"))
        reply = rcon.command(command)
        if expected:
            ok = re.search(expected, reply) is not None
            results.append((f"{path.name}:{number} {command}", ok, reply))
    return results


def cmd_test(args) -> int:
    validator = subprocess.run([sys.executable, str(REPO / "tools" / "validate.py")])
    if validator.returncode != 0 and not args.ignore_validate:
        print("Static validation failed; fix it first (or pass --ignore-validate)")
        return 1
    started_here = False
    if not is_running():
        if cmd_start(args) != 0:
            return 1
        started_here = True
    try:
        rcon = connect(retries=5)
        errors = reload_and_check(rcon)
        report_load_errors(errors)
        script_log_offset = log_size(KUBEJS_LOG_FILE)
        results = run_builtin_checks(rcon)
        files = [Path(f) for f in args.files] if args.files else pack_sources.test_files()
        for test_file in files:
            results += run_test_file(rcon, test_file)
        rcon.close()
        runtime = kubejs_errors(log_since(script_log_offset, KUBEJS_LOG_FILE))
        results.append(("no script errors or engine warnings while testing", not runtime, "\n        ".join(runtime)))
    finally:
        if started_here and not args.keep:
            cmd_stop(args)
    failed = [r for r in results if not r[1]]
    for name, ok, reply in results:
        if not ok or args.verbose:
            print(f"{'PASS' if ok else 'FAIL'}  {name}\n        reply: {reply or '(empty)'}")
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed, {len(errors)} load error(s)")
    return 1 if failed or errors else 0


# ---------- dev client world ----------

def cmd_client_world(args) -> int:
    """Prepare run/ for `gradlew runClient`: a flat world with cheats on, the pack synced, scripts linked."""
    dest = CLIENT_SAVES_DIR / CLIENT_WORLD_NAME
    if args.fresh and dest.exists():
        shutil.rmtree(dest)
    if not dest.exists():
        generate_server_world()
        shutil.copytree(WORLD_DIR, dest, ignore=shutil.ignore_patterns("session.lock", "datapacks"))
        enable_cheats(dest / "level.dat")
        print(f"Created client test world {dest}")
    copy_pack(dest / "datapacks" / PACK_ID)
    print(f"Synced the pack into {dest / 'datapacks' / PACK_ID}")
    link_client_scripts()
    link_into_client(CLIENT_RESOURCEPACK_LINK, RESOURCEPACK_DIR)
    link_into_client(CLIENT_EDITOR_EXPORT_LINK, RESOURCEPACK_DIR / "assets" / PACK_ID)
    enable_client_resource_pack()
    write_dev_run_config(args)
    return 0


def write_dev_run_config(args):
    """A scripted run (quit-after, join-timeout or commands) gets a config the dev client script obeys."""
    CLIENT_DEV_SCRIPT_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEV_CLIENT_SCRIPT, CLIENT_DEV_SCRIPT_DEST)
    # NBTIO.write (the !photon_dump step) does not create folders.
    (CLIENT_DIR / "photon_dump").mkdir(exist_ok=True)
    scripted = args.quit_after or args.join_timeout or args.commands
    if not scripted:
        CLIENT_DEV_CONFIG.unlink(missing_ok=True)
        return
    config = {
        "quitAfterSeconds": args.quit_after or 0,
        "joinTimeoutSeconds": args.join_timeout or DEFAULT_JOIN_TIMEOUT_S,
        "commands": [c.strip() for c in (args.commands or "").split("|") if c.strip()],
    }
    CLIENT_DEV_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CLIENT_DEV_CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Scripted run: {config}")


def link_client_scripts():
    """run/kubejs/server_scripts is a real folder holding two links: the shared scripts and origins/. KubeJS only
    loads .js, so an origin's effects, tests and data beside its scripts are ignored there."""
    if CLIENT_SCRIPTS_LINK.is_junction() or CLIENT_SCRIPTS_LINK.is_symlink():
        os.rmdir(CLIENT_SCRIPTS_LINK) if os.name == "nt" else CLIENT_SCRIPTS_LINK.unlink()
    CLIENT_SCRIPTS_LINK.mkdir(parents=True, exist_ok=True)
    for entry in SCRIPTS_DIR.iterdir():
        if entry.is_dir():
            link_into_client(CLIENT_SCRIPTS_LINK / entry.name, entry)
    pack_sources.ORIGINS_DIR.mkdir(exist_ok=True)
    link_into_client(CLIENT_SCRIPTS_LINK / pack_sources.ORIGIN_SCRIPTS_PREFIX, pack_sources.ORIGINS_DIR)


def link_into_client(link: Path, target: Path):
    """The dev client reads repo folders through junctions, so an edit plus /reload (or F3+T) is enough."""
    if link.is_junction() or link.is_symlink():
        return
    if link.exists():
        shutil.rmtree(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, stdout=subprocess.DEVNULL)
    else:
        link.symlink_to(target, target_is_directory=True)
    print(f"Linked {link} -> {target}")


def enable_client_resource_pack():
    lines = CLIENT_OPTIONS.read_text(encoding="utf-8").splitlines() if CLIENT_OPTIONS.exists() else []
    for index, line in enumerate(lines):
        if line.startswith(RESOURCE_PACKS_OPTION):
            packs = json.loads(line[len(RESOURCE_PACKS_OPTION):])
            if CLIENT_PACK_ENTRY in packs:
                return
            lines[index] = RESOURCE_PACKS_OPTION + json.dumps(packs + [CLIENT_PACK_ENTRY], separators=(",", ":"))
            break
    else:
        lines.append(RESOURCE_PACKS_OPTION + json.dumps(["vanilla", "mod_resources", CLIENT_PACK_ENTRY],
                                                        separators=(",", ":")))
    CLIENT_OPTIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Enabled the {PACK_ID} resource pack in {CLIENT_OPTIONS}")


def generate_server_world():
    if not (SERVER_DIR / "run.bat").exists():
        raise SystemExit("test server is not set up; run: python tools/testserver.py setup")
    if is_running():
        connect().command("save-all flush")
        return
    if (WORLD_DIR / "level.dat").exists():
        return
    print("Generating the test world with the test server (one time)...")
    if cmd_start(argparse.Namespace()) != 0:
        raise SystemExit("could not start the test server to generate the world")
    cmd_stop(argparse.Namespace())


def enable_cheats(level_dat: Path):
    with gzip.open(level_dat, "rb") as f:
        data = bytearray(f.read())
    marker = ALLOW_COMMANDS_TAG
    index = data.find(marker)
    if index < 0:
        raise SystemExit(f"{level_dat} has no allowCommands tag")
    data[index + len(marker)] = 1
    with gzip.open(level_dat, "wb") as f:
        f.write(data)


# ---------- shipping ----------

def cmd_deploy(args) -> int:
    save = INSTANCE_DIR / "saves" / args.save
    if not save.is_dir():
        names = sorted(p.name for p in (INSTANCE_DIR / "saves").iterdir() if p.is_dir())
        raise SystemExit(f"no save '{args.save}'. Saves: {', '.join(names) or '(none)'}")
    dest = save / "datapacks" / PACK_ID
    copy_pack(dest)
    print(f"Copied the datapack to {dest}. The domain engine also needs KubeJS in that instance and the")
    print("scripts from dist/ordertest-kubejs.zip (python tools/testserver.py zip). In game run /reload.")
    return 0


def cmd_zip(args) -> int:
    DIST_DIR.mkdir(exist_ok=True)
    pack_zip = DIST_DIR / f"{PACK_ID}.zip"
    with zipfile.ZipFile(pack_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, src in pack_sources.datapack_files().items():
            z.write(src, rel)
    scripts_zip = DIST_DIR / f"{PACK_ID}-kubejs.zip"
    with zipfile.ZipFile(scripts_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, src in pack_sources.script_files().items():
            z.write(src, "kubejs/server_scripts/" + rel)
    resources_zip = DIST_DIR / f"{PACK_ID}-resources.zip"
    with zipfile.ZipFile(resources_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for file in sorted(RESOURCEPACK_DIR.rglob("*")):
            if file.is_file() and file.suffix != ".md":
                # A fixed timestamp keeps the SHA-1 the same until a file's content changes, so players only
                # download the pack again when something in it really changed.
                # Stored, not deflated: compressed bytes can differ between zlib builds, which would give the same
                # pack a different SHA-1 here and in CI. The .fx files are gzipped already.
                entry = zipfile.ZipInfo(file.relative_to(RESOURCEPACK_DIR).as_posix(), date_time=FIXED_ZIP_TIME)
                entry.compress_type = zipfile.ZIP_STORED
                z.writestr(entry, file.read_bytes())
    sha1 = hashlib.sha1(resources_zip.read_bytes()).hexdigest()
    print(f"Wrote {pack_zip} (datapack: world/datapacks/)")
    print(f"Wrote {scripts_zip} (KubeJS scripts: unzip into the server folder)")
    print(f"Wrote {resources_zip} (resource pack: host it and point server.properties at it)")
    print(f"  resource-pack-sha1={sha1}")
    return 0


BUNDLE_DIR = DIST_DIR / "server-upload"
# Tested jars (from gradlew installServerMods) under the names their download sites use, so a duplicate already
# on the server is easy to spot. Rhino, Architectury, Origins and Caelus are often there already.
BUNDLE_MODS = {
    "photon-": ("mods", "photon-forge-1.20.1-1.1.17.jar"),
    "kubejs-": ("mods", "kubejs-forge-2001.6.5-build.26.jar"),
    "rhino-": ("mods-only-if-missing", "rhino-forge-2001.2.3-build.10.jar"),
    "architectury-api-": ("mods-only-if-missing", "architectury-9.2.14-forge.jar"),
    "origins-forge-": ("mods-only-if-missing", "origins-forge-1.20.1-1.10.0.9-all.jar"),
    "caelus-": ("mods-only-if-missing", "caelus-forge-3.2.0+1.20.1.jar"),
}
BUNDLE_GUIDE = """Order test: server upload
=========================
Everything here was built on the dev PC. The server needs no Python, only these files.

1. mods/                    -> copy into the server's mods/ folder.
2. mods-only-if-missing/    -> copy a jar into mods/ ONLY if the server has no version of that mod yet
                               (two copies of one mod stop the server from starting).
3. kubejs/                  -> copy into the server folder (it creates kubejs/server_scripts/ordertest/).
4. world/datapacks/         -> copy ordertest.zip into <your world folder>/datapacks/
                               (the world folder is named by level-name in server.properties, usually world).
5. HOST-THIS/ordertest-resources.zip -> upload anywhere with a direct download link (a GitHub release works),
   then add these lines to server.properties:

       resource-pack=<the direct download link>
       resource-pack-sha1={sha1}
       require-resource-pack=true

6. player-mods/             -> every player puts this jar in their mods/ folder, once.
7. Restart the server. The console shows "Photon is initializing on platform: Forge". An error about
   "FXEditor for invalid dist DEDICATED_SERVER" right after it is normal.

Updating: new scripts -> replace kubejs/server_scripts/ordertest/ and run /reload.
New effects -> upload the new ordertest-resources.zip, put its new SHA-1 in server.properties, restart.
"""


def cmd_bundle(args) -> int:
    """Lay out everything the server needs as files to upload; nothing in it needs Python."""
    if cmd_zip(args) != 0:
        return 1
    sources = sorted((SERVER_DIR / "mods").glob("*.jar"))
    if not sources:
        raise SystemExit("no tested mod jars yet; run: python tools/testserver.py setup")
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    for prefix, (folder, name) in BUNDLE_MODS.items():
        jar = next((j for j in sources if j.name.startswith(prefix)), None)
        if not jar:
            raise SystemExit(f"no {prefix}*.jar in {SERVER_DIR / 'mods'}; run: gradlew installServerMods")
        (BUNDLE_DIR / folder).mkdir(parents=True, exist_ok=True)
        shutil.copy2(jar, BUNDLE_DIR / folder / name)
        if prefix == "photon-":
            (BUNDLE_DIR / "player-mods").mkdir(exist_ok=True)
            shutil.copy2(jar, BUNDLE_DIR / "player-mods" / name)
    copy_files(pack_sources.script_files(), BUNDLE_DIR / "kubejs" / "server_scripts")
    (BUNDLE_DIR / "world" / "datapacks").mkdir(parents=True)
    shutil.copy2(DIST_DIR / f"{PACK_ID}.zip", BUNDLE_DIR / "world" / "datapacks" / f"{PACK_ID}.zip")
    (BUNDLE_DIR / "HOST-THIS").mkdir()
    resources = DIST_DIR / f"{PACK_ID}-resources.zip"
    shutil.copy2(resources, BUNDLE_DIR / "HOST-THIS" / resources.name)
    sha1 = hashlib.sha1(resources.read_bytes()).hexdigest()
    (BUNDLE_DIR / "SERVER-SETUP.txt").write_text(BUNDLE_GUIDE.format(sha1=sha1), encoding="utf-8")
    print(f"Ready to upload: {BUNDLE_DIR} (steps in SERVER-SETUP.txt)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("setup"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_setup)
    sub.add_parser("start").set_defaults(func=cmd_start)
    sub.add_parser("stop").set_defaults(func=cmd_stop)
    sub.add_parser("sync").set_defaults(func=cmd_sync)
    p = sub.add_parser("rcon"); p.add_argument("command", nargs="+"); p.set_defaults(func=cmd_rcon)
    p = sub.add_parser("test")
    p.add_argument("files", nargs="*", help="specific .mctest files (default: tests/*.mctest)")
    p.add_argument("--keep", action="store_true", help="leave the server running if test started it")
    p.add_argument("--verbose", "-v", action="store_true", help="print passing checks too")
    p.add_argument("--ignore-validate", action="store_true")
    p.set_defaults(func=cmd_test)
    p = sub.add_parser("deploy"); p.add_argument("save"); p.set_defaults(func=cmd_deploy)
    sub.add_parser("zip").set_defaults(func=cmd_zip)
    sub.add_parser("bundle", help="build dist/server-upload/, everything the server needs").set_defaults(func=cmd_bundle)
    p = sub.add_parser("client-world", help="prepare run/saves for gradlew runClient")
    p.add_argument("--fresh", action="store_true", help="recreate the world from scratch")
    p.add_argument("--quit-after", type=int, help="quit the dev client this many seconds after joining")
    p.add_argument("--join-timeout", type=int, help=f"quit if the world is not reached (default {DEFAULT_JOIN_TIMEOUT_S})")
    p.add_argument("--commands", help="'|'-separated commands (/...) or chat lines to send after joining")
    p.set_defaults(func=cmd_client_world)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
