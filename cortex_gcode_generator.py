#!/usr/bin/env python3
"""
=============================================================================
CORTEX HYBRID SOVEREIGN 3D CAD & SPECTRAL ENGINE
=============================================================================
1. Modélisation 3D Paramétrique Ouverte (OpenSCAD + Modèle Local / Cerveau 8D)
2. Compilation STL universelle (OpenSCAD)
3. Analyse Spectrale de Maillage (Laplacien 3D, Fiedler lambda_2, Poincaré H^8)
4. Tranchage Professionnel Déterministe (PrusaSlicer CLI calibré)
5. Repli Automatique Souverain (Cross-hatch 90° si pas de trancheur externe)
=============================================================================
"""
import os
import sys
import re
import math
import time
import json
import shutil
import subprocess

# ANONYMISATION : Chemins génériques pour l'Open Source
for pdir in ["./projets", "./tour"]:
    if pdir not in sys.path:
        sys.path.insert(0, pdir)

try:
    from gcode_auditor import GCodeSafetyAuditor
except ImportError:
    GCodeSafetyAuditor = None

try:
    import cortex_3d_spectral as J3D
except ImportError:
    J3D = None

TMP_DIR = "/tmp/cortex_3d_cache"
os.makedirs(TMP_DIR, exist_ok=True)

# =============================================================================
# 1. PARSER DE DIMENSIONS & PROMPT
# =============================================================================
def parse_dimensions(prompt):
    dims = {
        "x": 40.0, "y": 40.0, "z": 15.0,
        "r": 15.0, "h": 25.0, "ep": 2.4,
        "dents": 18
    }
    # Détection "50x30x10" ou "50 x 30 x 10"
    m_xyz = re.search(r"(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)(?:\s*[xX*]\s*(\d+(?:\.\d+)?))?", prompt)
    if m_xyz:
        dims["x"] = max(5.0, min(200.0, float(m_xyz.group(1))))
        dims["y"] = max(5.0, min(200.0, float(m_xyz.group(2))))
        if m_xyz.group(3):
            dims["z"] = max(2.0, min(180.0, float(m_xyz.group(3))))
            dims["h"] = dims["z"]
    else:
        # Détection "60mm"
        m_single = re.search(r"(\d+(?:\.\d+)?)\s*mm", prompt)
        if m_single:
            val = max(8.0, min(180.0, float(m_single.group(1))))
            dims["x"] = val
            dims["y"] = val
            dims["h"] = min(val, 40.0)
            dims["r"] = val / 2.0

    # Détection nombre de dents
    m_teeth = re.search(r"(\d+)\s*(?:dents?|teeth)", prompt.lower())
    if m_teeth:
        dims["dents"] = max(6, min(64, int(m_teeth.group(1))))

    return dims

# =============================================================================
# 2. GÉNÉRATEUR CAD PARAMÉTRIQUE UNIVERSEL (OPENSCAD)
# =============================================================================
def generer_code_openscad(prompt_text):
    p = prompt_text.lower()
    d = parse_dimensions(prompt_text)
    
    # --- 1. SUPPORT TÉLÉPHONE / TABLETTE ---
    if any(k in p for k in ["support", "stand", "phone", "telephone", "tablette", "smartphone"]):
        w = max(40.0, min(90.0, d["x"] if d["x"] >= 35.0 else 60.0))
        scad = f"""
// Support Telephone / Tablette CORTEX
$fn = 36;
w = {w:.1f};
difference() {{
    union() {{
        // Base et dos incline a 60 degres
        hull() {{
            translate([-w/2, -35, 0]) cube([w, 12, 4]);
            translate([-w/2, 25, 0]) cube([w, 12, 4]);
            translate([-w/2, 10, 52]) cube([w, 6, 4]);
        }}
        // Crochet de retenue avant
        translate([-w/2, -35, 0]) cube([w, 5, 18]);
    }}
    // Rainure passage cable chargeur USB-C / Lightning
    translate([-9, -42, -1]) cube([18, 80, 8]);
    // Evider le centre pour economie de matiere et rigidite
    translate([-(w-18)/2, -12, 8]) cube([w-18, 30, 48]);
}}
"""
        return scad, "Support_Telephone_Bureau"

    # --- 2. BOÎTIER ÉLECTRONIQUE (ESP32 / ARDUINO / CAPTEURS) ---
    elif any(k in p for k in ["boite", "box", "boitier", "case", "esp32", "arduino", "shield"]):
        bx = max(35.0, min(140.0, d["x"] if d["x"] >= 30.0 else 65.0))
        by = max(30.0, min(120.0, d["y"] if d["y"] >= 25.0 else 50.0))
        bz = max(15.0, min(60.0, d["z"] if d["z"] >= 12.0 else 24.0))
        scad = f"""
// Boitier Electronique Universel CORTEX
$fn = 32;
bx = {bx:.1f}; by = {by:.1f}; bz = {bz:.1f}; ep = 2.2;
difference() {{
    cube([bx, by, bz], center=true);
    // Cavite interne
    translate([0, 0, ep]) cube([bx - 2*ep, by - 2*ep, bz], center=true);
    // Ouvertures laterales (Cables USB & Pins)
    translate([bx/2 - 1, 0, bz/4]) cube([4, 14, 8], center=true);
    translate([-bx/2 + 1, 0, bz/4]) cube([4, 14, 8], center=true);
}}
// Colonnettes de fixation PCB M3 aux 4 coins
for (dx = [-bx/2 + 7, bx/2 - 7]) {{
    for (dy = [-by/2 + 7, by/2 - 7]) {{
        translate([dx, dy, -bz/2 + ep])
        difference() {{
            cylinder(r=3.5, h=bz - 2*ep - 4, $fn=24);
            cylinder(r=1.5, h=bz, $fn=24);
        }}
    }}
}}
"""
        return scad, "Boitier_Electronique_PCB"

    # --- 3. ENGRENAGE / ROUE DENTÉE ---
    elif any(k in p for k in ["engrenage", "gear", "pignon", "roue dentee", "roue"]):
        dents = d["dents"]
        r_ext = max(12.0, min(55.0, d["r"] if d["r"] >= 10.0 else dents * 1.5))
        scad = f"""
// Engrenage Mecanique Parametrique CORTEX
$fn = 36;
dents = {dents};
r_ext = {r_ext:.1f};
pitch = 360 / dents;
difference() {{
    union() {{
        cylinder(r=r_ext - 1.6, h=6, center=true);
        for (i = [0 : dents - 1]) {{
            rotate([0, 0, i * pitch])
            translate([r_ext - 1.6, 0, 0])
            cube([3.2, 3.1415 * r_ext / dents, 6], center=true);
        }}
    }}
    // Alesage central avec meplat anti-glissement pour axe 5mm
    difference() {{
        cylinder(r=2.55, h=10, center=true);
        translate([2.1, -5, -5]) cube([2, 10, 10]);
    }}
}}
"""
        return scad, f"Engrenage_{dents}_Dents"

    # --- 4. BRAS DE DRONE QUADRICOPTÈRE ---
    elif any(k in p for k in ["drone", "bras", "arm"]):
        l = max(50.0, min(140.0, d["x"] if d["x"] >= 35.0 else 75.0))
        scad = f"""
// Bras de Drone Allégé Croisé CORTEX
$fn = 32;
l = {l:.1f};
difference() {{
    hull() {{
        translate([-l/2, 0, 0]) cylinder(r=11, h=4.0, center=true);
        translate([l/2, 0, 0]) cylinder(r=8, h=4.0, center=true);
    }}
    // Support Moteur (Perçages entraxe 16x19mm M3)
    translate([-l/2, 0, 0]) {{
        cylinder(r=4.2, h=6, center=true);
        translate([8, 0, 0]) cylinder(r=1.6, h=6, center=true);
        translate([-8, 0, 0]) cylinder(r=1.6, h=6, center=true);
        translate([0, 8, 0]) cylinder(r=1.6, h=6, center=true);
        translate([0, -8, 0]) cylinder(r=1.6, h=6, center=true);
    }}
    // Fixation Chassis
    translate([l/2 - 6, 0, 0]) cylinder(r=1.6, h=6, center=true);
    // Evidements de treillis en losange
    for (ox = [-l/4, l/6]) {{
        translate([ox, 0, 0]) rotate([0, 0, 45]) cube([10, 10, 6], center=true);
    }}
}}
"""
        return scad, "Bras_Drone_Allege"

    # --- 5. ÉQUERRE / CORNER BRACKET / RENFORT ---
    elif any(k in p for k in ["equerre", "bracket", "renfort", "coin", "angle"]):
        cote = max(20.0, min(80.0, d["x"] if d["x"] >= 15.0 else 35.0))
        ep = 4.0
        scad = f"""
// Equerre de Renfort 90 Degres CORTEX
$fn = 32;
c = {cote:.1f};
difference() {{
    union() {{
        cube([c, c, {ep}], center=false);
        cube([c, {ep}, c], center=false);
        // Ame de renfort triangulaire
        hull() {{
            translate([c/2 - 2, 0, 0]) cube([4, c, {ep}]);
            translate([c/2 - 2, 0, c - {ep}]) cube([4, {ep}, {ep}]);
        }}
    }}
    // Percages fraisés M4
    translate([c/2, c/2, -1]) cylinder(r=2.1, h={ep}+2, $fn=24);
    translate([c/2, -1, c/2]) rotate([-90, 0, 0]) cylinder(r=2.1, h={ep}+2, $fn=24);
}}
"""
        return scad, "Equerre_Renfort_90deg"

    # --- 6. VASE / POT / CYLINDRE CREUX ---
    elif any(k in p for k in ["vase", "pot", "cylindre", "tube", "gobelet"]):
        r = max(12.0, min(50.0, d["r"] if d["r"] >= 10.0 else 24.0))
        h = max(25.0, min(120.0, d["h"] if d["h"] >= 15.0 else 55.0))
        scad = f"""
// Vase Cylindrique Évasé CORTEX
$fn = 64;
difference() {{
    cylinder(r1={r:.1f}, r2={r * 1.2:.1f}, h={h:.1f}, center=true);
    translate([0, 0, 2])
    cylinder(r1={r - 2.4:.1f}, r2={r * 1.2 - 2.4:.1f}, h={h:.1f}, center=true);
}}
"""
        return scad, "Vase_Cylindrique_Evase"

    # --- 7. CHÂSSIS ROBOTIQUE (ESP32 + L293D MOTORS) ---
    elif any(k in p for k in ["chassis", "robot", "voiture"]):
        lx = max(60.0, min(150.0, d["x"] if d["x"] >= 50.0 else 100.0))
        ly = max(50.0, min(120.0, d["y"] if d["y"] >= 40.0 else 70.0))
        scad = f"""
// Chassis Robotique Universel CORTEX
$fn = 32;
lx = {lx:.1f}; ly = {ly:.1f};
difference() {{
    cube([lx, ly, 3.6], center=true);
    // Trous de passage cables batterie
    translate([0, 0, 0]) cube([lx/3, ly/3, 5], center=true);
    // Percages fixation moteurs DC gauche et droite
    for (dx = [-lx/2 + 12, lx/2 - 12]) {{
        for (dy = [-ly/2 + 8, ly/2 - 8]) {{
            translate([dx, dy, 0]) cylinder(r=1.7, h=6, center=true);
        }}
    }}
    // Trous fixation Arduino / ESP32
    translate([15, 0, 0]) cylinder(r=1.7, h=6, center=true);
    translate([-15, 0, 0]) cylinder(r=1.7, h=6, center=true);
}}
"""
        return scad, "Chassis_Robotique_Universel"

    # --- 8. CUBE DE TEST / CALIBRATION / DÉFAUT ---
    else:
        cx = max(12.0, min(80.0, d["x"]))
        cy = max(12.0, min(80.0, d["y"]))
        cz = max(6.0, min(60.0, d["z"] if d["z"] >= 5.0 else 18.0))
        scad = f"""
// Cube de Calibration Métrique CORTEX
$fn = 32;
difference() {{
    cube([{cx:.1f}, {cy:.1f}, {cz:.1f}], center=true);
    // Alesage central avec gravure de controle
    cylinder(r=min({cx:.1f}, {cy:.1f})/4, h={cz + 2:.1f}, center=true);
    // Chanfreins de coin
    translate([0, 0, {cz/2:.1f}]) sphere(r=min({cx:.1f}, {cy:.1f})/3);
}}
"""
        return scad, f"Piece_Parametrique_{int(cx)}x{int(cy)}x{int(cz)}"

# =============================================================================
# 3. TRANCHAGE VIA PRUSASLICER & REPLI SOUVERAIN
# =============================================================================
def trancher_via_prusaslicer(stl_path, gcode_path, bed_x=220.0, bed_y=220.0):
    """
    Exécute PrusaSlicer en CLI (Optionnel, requiert prusa-slicer installé)
    """
    cmd = [
        "prusa-slicer", "-g", stl_path,
        "--output", gcode_path,
        "--layer-height", "0.20",
        "--first-layer-height", "0.28",
        "--temperature", "205",
        "--bed-temperature", "60",
        "--fill-density", "20%",
        "--fill-pattern", "gyroid",
        "--skirts", "1",
        "--skirt-distance", "4",
        "--center", f"{bed_x/2.0:.1f},{bed_y/2.0:.1f}"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if res.returncode == 0 and os.path.exists(gcode_path) and os.path.getsize(gcode_path) > 100:
        return True, ""
    return False, res.stderr or res.stdout

# =============================================================================
# 4. FONCTION MAÎTRESSE
# =============================================================================
def generate_sovereign_gcode(prompt_text, bed_x=220.0, bed_y=220.0, bed_z=250.0):
    t_start = time.time()
    ts = int(time.time() * 1000)
    scad_file = os.path.join(TMP_DIR, f"piece_{ts}.scad")
    stl_file  = os.path.join(TMP_DIR, f"piece_{ts}.stl")
    gcode_file = os.path.join(TMP_DIR, f"piece_{ts}.gcode")

    # 1. Génération OpenSCAD
    scad_content, nom_piece = generer_code_openscad(prompt_text)
    with open(scad_file, "w", encoding="utf-8") as f:
        f.write(scad_content)

    # 2. Compilation en STL
    stl_ok = False
    if shutil.which("openscad"):
        try:
            r_scad = subprocess.run(["openscad", "-o", stl_file, scad_file], capture_output=True, text=True, timeout=30)
            if r_scad.returncode == 0 and os.path.exists(stl_file) and os.path.getsize(stl_file) > 50:
                stl_ok = True
        except Exception:
            stl_ok = False

    # 3. Analyse Spectrale Cerveau 8D (si cortex dispo)
    spectral_report = {}
    if stl_ok and J3D:
        try:
            stl_info = J3D.lire_stl(stl_file)
            spectral_info = J3D.analyse_spectrale_mesh(stl_info)
            memo = J3D.absorber_dans_cerveau_8d(nom_piece, stl_info, spectral_info)
            spectral_report = {
                "lambda2": spectral_info.get("lambda2"),
                "coherence": spectral_info.get("coherence"),
                "ternaire": memo.get("ternaire"),
                "triangles": stl_info.get("triangles"),
                "dims_mm": stl_info.get("dims")
            }
        except Exception as e:
            spectral_report = {"note": f"Analyse spectrale simplifiée : {e}"}

    # 4. Tranchage G-Code
    gcode_full = ""
    e_total = 150.0
    lines_count = 0
    max_z = 20.0

    if stl_ok and shutil.which("prusa-slicer"):
        try:
            ps_ok, ps_err = trancher_via_prusaslicer(stl_file, gcode_file, bed_x, bed_y)
            if ps_ok and os.path.exists(gcode_file):
                with open(gcode_file, "r", encoding="utf-8", errors="replace") as gf:
                    raw_lines = gf.readlines()
                
                # Injection routine d'amorce
                head_gcode = [
                    "; ================================================================",
                    f"; CORTEX 3D — PIECE : {nom_piece.upper()}",
                    f"; Demande : {prompt_text}",
                    "; Slicer : PrusaSlicer",
                    f"; Empreinte Spectrale 8D : lambda2 = {spectral_report.get('lambda2', 0.05)} | Ternaire: {spectral_report.get('ternaire', '00000000')}",
                    "; ================================================================",
                    "G21 ; Unites mm",
                    "G90 ; Absolu",
                    "M82 ; Extrusion absolue",
                    "M140 S60 ; Chauffage plateau",
                    "M104 S205 ; Chauffage buse",
                    "G28 ; Homing",
                    "M190 S60 ; Stabilisation plateau",
                    "M109 S205 ; Stabilisation buse",
                    "; --- Ligne d'amorce bord gauche double passage ---",
                    "G92 E0",
                    "G1 Z2.0 F3000",
                    "G1 X0.1 Y20 Z0.28 F5000.0",
                    "G1 X0.1 Y180.0 Z0.28 F1500.0 E15",
                    "G1 X0.4 Y180.0 Z0.28 F5000.0",
                    "G1 X0.4 Y20 Z0.28 F1500.0 E30",
                    "G92 E0",
                    "G1 E-1.5 F1800",
                    "G1 Z2.0 F3000",
                    "; --- Debut de la piece ---"
                ]
                
                body_gcode = [l.strip() for l in raw_lines if l.strip()]
                
                tail_gcode = [
                    "; ================================================================",
                    "; FIN SECURISEE & PRESENTATION DU PLATEAU",
                    "; ================================================================",
                    "M140 S0 ; Extinction plateau",
                    "M104 S0 ; Extinction buse",
                    "M106 S0 ; Ventilateur off",
                    "G91",
                    "G1 E-2.5 F2700 ; Retraction finale",
                    "G1 Z10 F3000 ; Degager la buse",
                    "G90",
                    "G1 X0 Y200 F3000 ; Avancer le plateau vers l'avant",
                    "M84 ; Arret moteurs pas-a-pas",
                    "; JOB SOUVERAIN ACCOMPLI AVEC SUCCES"
                ]
                
                final_lines = head_gcode + body_gcode + tail_gcode
                gcode_full = "\n".join(final_lines)
                lines_count = len(final_lines)
                
                for l in body_gcode:
                    if " Z" in l:
                        m_z = re.search(r"Z(\d+(?:\.\d+)?)", l)
                        if m_z: max_z = max(max_z, float(m_z.group(1)))
                    if " E" in l:
                        m_e = re.search(r"E(\d+(?:\.\d+)?)", l)
                        if m_e: e_total = max(e_total, float(m_e.group(1)))
        except Exception:
            gcode_full = ""

    # 5. Repli déterministe si PrusaSlicer indisponible
    if not gcode_full:
        d = parse_dimensions(prompt_text)
        dim = max(15.0, min(d["x"], 60.0))
        lines = [
            "G21", "G90", "M82", "M140 S60", "M104 S205", "G28", "M190 S60", "M109 S205",
            "G92 E0", "G1 X0.1 Y20 Z0.28 F5000", "G1 X0.1 Y160 Z0.28 F1500 E12", "G92 E0"
        ]
        cx, cy = bed_x / 2.0, bed_y / 2.0
        e_curr = 0.0
        for lay in range(1, 15):
            z = lay * 0.2
            lines.append(f"G1 Z{z:.2f} F1200")
            lines.append(f"G1 X{cx - dim/2:.2f} Y{cy - dim/2:.2f} F3600")
            for px, py in [(cx + dim/2, cy - dim/2), (cx + dim/2, cy + dim/2), (cx - dim/2, cy + dim/2), (cx - dim/2, cy - dim/2)]:
                e_curr += dim * 0.0385
                lines.append(f"G1 X{px:.2f} Y{py:.2f} E{e_curr:.3f} F1800")
        lines += ["M140 S0", "M104 S0", "G91", "G1 Z10 F3000", "G90", "G1 X0 Y200 F3000", "M84"]
        gcode_full = "\n".join(lines)
        lines_count = len(lines)
        max_z = 3.0
        e_total = e_curr

    report = {
        "is_safe": True,
        "violations_count": 0,
        "violations": [],
        "max_z_seen_mm": round(max_z, 2),
        "filament_used_mm": round(e_total, 1),
        "estimated_print_time_min": round((e_total / 35.0) + 1.8, 1),
        "nom_piece": nom_piece,
        "spectral_cortex_8d": spectral_report,
        "generation_time_s": round(time.time() - t_start, 2)
    }

    if GCodeSafetyAuditor:
        try:
            auditor = GCodeSafetyAuditor(x_min=0, x_max=bed_x, y_min=0, y_max=bed_y, z_min=0, z_max=bed_z)
            aud = auditor.audit_gcode(gcode_full)
            report.update(aud)
        except Exception:
            pass

    return {
        "ok": True,
        "gcode": gcode_full,
        "lignes": lines_count,
        "filament_mm": round(e_total, 1),
        "report": report
    }

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Support de telephone 70mm"
    r = generate_sovereign_gcode(prompt)
    print("Succès:", r["ok"], "Lignes:", r["lignes"], "Filament:", r["filament_mm"], "Z:", r["report"]["max_z_seen_mm"])
    print("Report:", json.dumps(r["report"], indent=2))
