#!/usr/bin/env python3
"""
PONT IMPRIMANTE 3D MARLIN
Support complet de streaming G-code, modélisation souveraine, 
audit de température en direct et arrêt d'urgence instantané.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
import time
import threading
import re
import json
import math
import glob
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = "/dev/ttyUSB0"
BAUD = 115200
BED = 220.0
SER = None

JOB = {
    "running": False,
    "objet": None,
    "ligne": 0,
    "total": 0,
    "stop": False,
    "msg": "prêt"
}

LAST_STATE = {
    "connected": False,
    "buse": [21.0, 0.0],
    "plateau": [21.0, 0.0],
    "xyz": [0.0, 0.0, 0.0],
    "status": "Attente connexion USB"
}

LOCK = threading.Lock()
SERIAL_LOCK = threading.Lock()
INJECT_QUEUE = []

def find_port():
    candidates = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"] + glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    for p in candidates:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            pass
    return None

def _open(force=False):
    global SER, PORT, LAST_STATE
    if force and SER:
        try:
            SER.close()
        except Exception:
            pass
        SER = None
    if SER and SER.is_open and not force:
        return SER
    p = find_port()
    if not p:
        SER = None
        LAST_STATE["connected"] = False
        return None
    PORT = p
    try:
        SER = serial.Serial(PORT, BAUD, timeout=0.5)
        time.sleep(2.0)
        SER.reset_input_buffer()
        got_reply = False
        for _ in range(3):
            SER.write(b"M105\n")
            time.sleep(0.3)
            r = SER.read(200)
            if b"T:" in r or b"ok" in r:
                got_reply = True
                break
        if got_reply:
            LAST_STATE["connected"] = True
            LAST_STATE["status"] = "En ligne"
        else:
            LAST_STATE["connected"] = False
            LAST_STATE["status"] = "Câble USB détecté, allumez l'alimentation 24V"
        return SER
    except Exception:
        SER = None
        LAST_STATE["connected"] = False
        LAST_STATE["status"] = "Erreur port série USB"
        return None

def _read_cmd(s, stop_tokens=("ok",), timeout=0.8):
    if not s:
        return ""
    buf = []
    t = time.time()
    while time.time() - t < timeout:
        try:
            line = s.readline().decode("utf-8", "replace").strip()
        except Exception:
            break
        if not line:
            continue
        buf.append(line)
        if any(tok in line for tok in stop_tokens):
            break
    return "\n".join(buf)

def update_telemetry_from_serial():
    global LAST_STATE
    with SERIAL_LOCK:
        s = _open()
        if not s:
            LAST_STATE["connected"] = False
            LAST_STATE["status"] = "Attente connexion câble USB"
            return
        try:
            s.reset_input_buffer()
            s.write(b"M105\n")
            t = time.time()
            found_temp = False
            while time.time() - t < 1.0:
                try:
                    ln = s.readline().decode("utf-8", errors="replace").strip()
                except Exception:
                    break
                if not ln:
                    continue
                t_m = re.search(r"T:([\d.]+)\s*/([\d.]+)", ln)
                b_m = re.search(r"B:([\d.]+)\s*/([\d.]+)", ln)
                if t_m:
                    LAST_STATE["buse"] = [float(t_m.group(1)), float(t_m.group(2))]
                    found_temp = True
                if b_m:
                    LAST_STATE["plateau"] = [float(b_m.group(1)), float(b_m.group(2))]
                    found_temp = True
                if "ok" in ln.lower():
                    break
            
            if found_temp:
                LAST_STATE["connected"] = True
                LAST_STATE["status"] = "En ligne"
            elif not LAST_STATE["connected"]:
                LAST_STATE["status"] = "Port USB connecté mais imprimante muette"
        except Exception as e:
            LAST_STATE["connected"] = False
            LAST_STATE["status"] = f"Erreur USB: {str(e)[:40]}"

def telemetry_worker():
    while True:
        try:
            time.sleep(1.0)
            if not JOB["running"]:
                update_telemetry_from_serial()
        except Exception:
            time.sleep(1.0)

threading.Thread(target=telemetry_worker, daemon=True).start()

def send(g, to=3.0):
    global LAST_STATE
    cmd = g.split(";")[0].strip()
    if not cmd:
        return "ok"
        
    with SERIAL_LOCK:
        s = _open()
        if not s:
            return "ok (simule)"
        try:
            s.write((cmd + "\n").encode())
        except Exception:
            s = _open(force=True)
            if not s:
                return "err (port deconnecte)"
            try:
                s.write((cmd + "\n").encode())
            except Exception:
                return "err (port inaccessible)"
                
        t = time.time()
        resp = []
        silent_count = 0
        while time.time() - t < to:
            try:
                ln = s.readline().decode("utf-8", "replace").strip()
            except Exception:
                time.sleep(0.02)
                continue
            if not ln:
                silent_count += 1
                if silent_count > 4 and len(resp) == 0:
                    break
                continue
            silent_count = 0
            resp.append(ln)
            
            t_m = re.search(r"T:([\d.]+)\s*/([\d.]+)", ln)
            b_m = re.search(r"B:([\d.]+)\s*/([\d.]+)", ln)
            if t_m:
                LAST_STATE["buse"] = [float(t_m.group(1)), float(t_m.group(2))]
                LAST_STATE["connected"] = True
            if b_m:
                LAST_STATE["plateau"] = [float(b_m.group(1)), float(b_m.group(2))]
                LAST_STATE["connected"] = True
                
            if "ok" in ln.lower() or "error" in ln.lower():
                LAST_STATE["connected"] = True
                break
                
        return "\n".join(resp) if resp else "err (pas de reponse imprimante)"

def thread_executer_gcode(lines, nom="Piece_Cortex"):
    global JOB, LAST_STATE
    JOB.update({
        "running": True,
        "objet": nom,
        "ligne": 0,
        "total": len(lines),
        "stop": False,
        "msg": "Initialisation du job..."
    })
    try:
        for i, raw_line in enumerate(lines):
            if JOB["stop"]:
                send("M112", 2)
                send("M104 S0", 2)
                send("M140 S0", 2)
                send("M106 S0", 2)
                send("M84", 2)
                JOB["msg"] = "STOP D'URGENCE"
                break
                
            cmd = raw_line.split(";")[0].strip()
            if not cmd:
                continue
                
            JOB["ligne"] = i + 1
            JOB["msg"] = cmd
            
            while INJECT_QUEUE:
                inj = INJECT_QUEUE.pop(0)
                send(inj, 5)

            if i % 40 == 0 or i == len(lines) - 1:
                pct = int((i + 1) * 100 / max(1, len(lines)))
                send(f"M117 CORTEX {pct}% {nom[:8]}", 2)

            timeout = 360 if any(h in cmd for h in ["M109", "M190"]) else 60
            r = send(cmd, to=timeout)
            if "error" in r.lower():
                JOB["msg"] = f"Avertissement: {r}"
                
        if not JOB["stop"]:
            JOB["msg"] = "Terminé avec succès"
    except Exception as e:
        JOB["msg"] = "Crash: " + str(e)
    finally:
        JOB["running"] = False

def imprimer(mots):
    lm = mots.lower()
    nom = "test"
    if "purge" in lm or "prime" in lm:
        lines = [
            "G92 E0", "G1 Z2.0 F3000",
            "G1 X0.1 Y20 Z0.3 F5000.0",
            "G1 X0.1 Y180.0 Z0.3 F1500.0 E15",
            "G1 X0.4 Y180.0 Z0.3 F5000.0",
            "G1 X0.4 Y20 Z0.3 F1500.0 E30",
            "G92 E0", "G1 Z2.0 F3000"
        ]
        nom = "Purge_Buse"
    elif "nivelage" in lm or "niveau" in lm or "mesh" in lm:
        lines = ["M140 S60", "M190 S60", "G28", "G29", "M500", "M140 S0"]
        nom = "Nivelage_Mesh"
    else:
        nom = "Piece_Cortex"
        try:
            import cortex_gcode_generator as CGG
            res = CGG.generate_sovereign_gcode(mots)
            lines = [l for l in res["gcode"].splitlines() if l.strip()]
        except Exception:
            lines = [
                "G21", "G90", "M82", "M140 S60", "M104 S205", "G28",
                "M190 S60", "M109 S205", "G92 E0", "G1 Z2.0 F3000",
                "G1 X0.1 Y20 Z0.3 F5000.0", "G1 X0.1 Y180.0 Z0.3 F1500.0 E15",
                "G1 X0.4 Y180.0 Z0.3 F5000.0", "G1 X0.4 Y20 Z0.3 F1500.0 E30",
                "G92 E0", "G1 E-1.5 F1800", "G1 Z0.2 F3000",
                "G1 X100 Y100 F3000", "G1 E0 F1800",
                "G1 X120 Y100 E0.77 F1800", "G1 X120 Y120 E1.54", "G1 X100 Y120 E2.31", "G1 X100 Y100 E3.08",
                "G91", "G1 E-2 F2700", "G1 Z10 F3000", "G90", "G1 X0 Y200 F3000", "M104 S0", "M140 S0", "M84"
            ]
            
    thread_executer_gcode(lines, nom)

class H(BaseHTTPRequestHandler):
    def _s(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self._s({"ok": True})

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        global JOB
        u = urlparse(self.path)
        path = u.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
        
        with LOCK:
            if path in ("/imprimer_raw", "/api/imprimer_gcode", "/print", "/api/impr_inject", "/inject"):
                if JOB["running"]:
                    return self._s({"ok": False, "err": "Une impression est déjà en cours !"}, 409)
                try:
                    data = json.loads(body)
                except Exception:
                    data = {"gcode": body, "nom": "Piece"}
                gcode_text = data.get("gcode", "")
                nom = data.get("nom", "Piece_Cortex")
                if not gcode_text.strip():
                    return self._s({"ok": False, "err": "G-code vide"}, 400)
                    
                lines = [l.strip() for l in gcode_text.splitlines() if l.strip() and not l.strip().startswith(";")]
                if not lines:
                    return self._s({"ok": False, "err": "Aucune commande exécutable"}, 400)
                    
                threading.Thread(target=thread_executer_gcode, args=(lines, nom), daemon=True).start()
                return self._s({"ok": True, "msg": f"Job « {nom} » lancé avec succès ({len(lines)} commandes)", "total": len(lines)})
                
        self._s({"err": "404"}, 404)

    def do_GET(self):
        global JOB, LAST_STATE
        u = urlparse(self.path)
        path = u.path
        qs = parse_qs(u.query)
        
        if path in ("/stop", "/api/impr_stop", "/api/stop"):
            if JOB["running"]:
                JOB["stop"] = True
            for c in ["M112", "M104 S0", "M140 S0", "M106 S0", "M84"]:
                send(c, 2)
            LAST_STATE["buse"][1] = 0.0
            LAST_STATE["plateau"][1] = 0.0
            return self._s({"ok": True, "msg": "STOP urgence envoyé, moteurs et chauffes désactivés"})
            
        if path in ("/job", "/api/impr_job", "/api/job"):
            return self._s(JOB)
        
        if path in ("/etat", "/api/impr_etat", "/api/etat"):
            res = dict(LAST_STATE)
            res["job"] = JOB
            return self._s(res)
            
        if "/dire" in path or "impr_dire" in path:
            if JOB["running"]:
                return self._s({"err": "Une impression est déjà en cours"})
            mots = qs.get("texte", [""])[0]
            threading.Thread(target=imprimer, args=(mots,), daemon=True).start()
            return self._s({"ok": "Processus démarré"})
            
        if path in ("/vitesse", "/api/impr_vitesse", "/api/vitesse"):
            val = int(qs.get("val", [100])[0])
            val = max(20, min(300, val))
            cmd = f"M220 S{val}"
            if JOB["running"]:
                INJECT_QUEUE.append(cmd)
                return self._s({"ok": True, "val": val, "queued": True, "msg": f"Vitesse {val}% injectée dans le flux Marlin"})
            else:
                r = send(cmd, 5)
                return self._s({"ok": True, "val": val, "resp": r})

        if path in ("/gcode", "/api/impr_gcode", "/api/gcode", "/api/impr_inject", "/inject"):
            cmd = qs.get("cmd", [""])[0] or qs.get("gcode", [""])[0]
            if not cmd:
                return self._s({"err": "cmd ou gcode manquante"})
            lines = [c.strip() for c in cmd.replace(";", "\n").splitlines() if c.strip()]
            outs = []
            for c in lines:
                outs.append(send(c, 30))
            return self._s({"ok": True, "out": "\n".join(outs)})

        if path in ("/move", "/api/impr_move", "/api/move"):
            axis = qs.get("axis", ["X"])[0].upper()
            dist = float(qs.get("dist", [0])[0])
            feed = int(qs.get("feed", [3000 if axis in ("X", "Y") else 600])[0])
            send("G91", 2)
            r = send(f"G1 {axis}{dist} F{feed}", 10)
            send("G90", 2)
            return self._s({"ok": True, "axis": axis, "dist": dist, "resp": r})

        if path in ("/home", "/api/impr_home", "/api/home"):
            axis = qs.get("axis", ["all"])[0].lower()
            cmd = "G28" if axis == "all" else f"G28 {axis.upper()}"
            r = send(cmd, 120)
            return self._s({"ok": True, "axis": axis, "resp": r})

        if path in ("/temp", "/api/impr_temp", "/api/temp"):
            buse = qs.get("buse", [None])[0]
            plateau = qs.get("plateau", [None])[0]
            outs = []
            if buse is not None:
                cmd = f"M104 S{float(buse):.0f}"
                if JOB["running"]:
                    INJECT_QUEUE.append(cmd)
                    outs.append("injecte_flux")
                else:
                    outs.append(send(cmd, 5))
                LAST_STATE["buse"][1] = float(buse)
            if plateau is not None:
                cmd = f"M140 S{float(plateau):.0f}"
                if JOB["running"]:
                    INJECT_QUEUE.append(cmd)
                    outs.append("injecte_flux")
                else:
                    outs.append(send(cmd, 5))
                LAST_STATE["plateau"][1] = float(plateau)
            return self._s({"ok": True, "buse": buse, "plateau": plateau, "resp": outs})

        if path in ("/fan", "/api/impr_fan", "/api/fan"):
            speed = int(qs.get("speed", [255])[0])
            r = send("M107", 2) if speed <= 0 else send(f"M106 S{speed}", 2)
            return self._s({"ok": True, "speed": speed, "resp": r})

        if path in ("/extrude", "/api/impr_extrude", "/api/extrude"):
            dist = float(qs.get("dist", [10])[0])
            feed = int(qs.get("feed", [150])[0])
            send("M83", 2)
            r = send(f"G1 E{dist} F{feed}", 20)
            send("M82", 2)
            return self._s({"ok": True, "dist": dist, "resp": r})

        if path in ("/motors", "/api/impr_motors", "/api/motors"):
            state = qs.get("state", ["off"])[0]
            r = send("M84" if state == "off" else "M17", 2)
            return self._s({"ok": True, "state": state, "resp": r})

        if path in ("/scan", "/api/impr_scan", "/api/scan"):
            s = _open()
            r = ""
            connected = False
            if s:
                try:
                    s.reset_input_buffer()
                    s.write(b"M115\n")
                    r = _read_cmd(s, stop_tokens=("ok", "FIRMWARE_NAME"), timeout=2.0)
                    connected = True
                except Exception:
                    pass
            return self._s({
                "connected": connected,
                "type": "Marlin 3D Printer Open Source",
                "firmware": r if connected else "Marlin 2.x (Attente USB)",
                "scan": r,
                "capacites": ["bed_leveling", "hotend_heating", "bed_heating", "fan_control", "linear_movement", "homing"],
                "statut": "En ligne" if connected else "En attente connexion physique USB"
            })

        self._s({"err": "404"}, 404)

if __name__ == "__main__":
    port = 7981
    print(f"PONT IMPRIMANTE SOUVERAIN -> http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
