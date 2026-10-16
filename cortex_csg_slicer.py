import math
import numpy as np

class SDFNode:
    """Nœud de base pour le Constructive Solid Geometry (Distance Signée)"""
    def dist(self, x, y, z):
        raise NotImplementedError

class Sphere(SDFNode):
    def __init__(self, cx, cy, cz, r):
        self.cx, self.cy, self.cz, self.r = cx, cy, cz, r
    def dist(self, x, y, z):
        return math.sqrt((x-self.cx)**2 + (y-self.cy)**2 + (z-self.cz)**2) - self.r

class Box(SDFNode):
    def __init__(self, cx, cy, cz, w, d, h):
        self.cx, self.cy, self.cz = cx, cy, cz
        self.hw, self.hd, self.hh = w/2, d/2, h/2
    def dist(self, x, y, z):
        dx = abs(x - self.cx) - self.hw
        dy = abs(y - self.cy) - self.hd
        dz = abs(z - self.cz) - self.hh
        length = math.sqrt(max(dx, 0)**2 + max(dy, 0)**2 + max(dz, 0)**2)
        return length + min(max(dx, max(dy, dz)), 0.0)

class Cylinder(SDFNode):
    def __init__(self, cx, cy, cz, r, h):
        self.cx, self.cy, self.cz = cx, cy, cz
        self.r, self.hh = r, h/2
    def dist(self, x, y, z):
        dx = abs(math.sqrt((x-self.cx)**2 + (y-self.cy)**2)) - self.r
        dz = abs(z - self.cz) - self.hh
        length = math.sqrt(max(dx, 0)**2 + max(dz, 0)**2)
        return length + min(max(dx, dz), 0.0)

class Union(SDFNode):
    def __init__(self, a, b):
        self.a, self.b = a, b
    def dist(self, x, y, z):
        return min(self.a.dist(x, y, z), self.b.dist(x, y, z))

class Subtract(SDFNode):
    def __init__(self, a, b):
        self.a, self.b = a, b
    def dist(self, x, y, z):
        return max(self.a.dist(x, y, z), -self.b.dist(x, y, z))

class CortexCSGSlicer:
    """Moteur de tranchage algorithmique basé sur les champs de distance mathématiques"""
    def __init__(self, obj: SDFNode, bounding_box):
        self.obj = obj
        self.bbox = bounding_box # (xmin, xmax, ymin, ymax, zmin, zmax)
        
    def slice_layer_contours(self, z, resolution=0.5):
        """
        Génère les périmètres d'une couche Z en utilisant une approche simple par grille.
        (Version prototype : génère un quadrillage plein pour l'instant)
        """
        xmin, xmax, ymin, ymax, _, _ = self.bbox
        points_inside = []
        
        # Scanner la grille 2D
        x = xmin
        while x <= xmax:
            y = ymin
            while y <= ymax:
                if self.obj.dist(x, y, z) <= 0:
                    points_inside.append((x, y))
                y += resolution
            x += resolution
            
        return points_inside

    def generate_gcode(self, filename, layer_height=0.2, nozzle=0.4):
        print(f"[CSG Engine] Début de l'imagination volumétrique vers {filename}...")
        zmin, zmax = self.bbox[4], self.bbox[5]
        layers = int((zmax - zmin) / layer_height)
        
        gcode = [
            "; --- Cortex CSG Engine V1 ---",
            "M140 S65", "M104 S210",
            "M190 S65", "M109 S210",
            "M221 S200",  # <--- BOOST EXTRUSION A 200%
            "G28", "G92 E0"
        ]
        
        # Logique d'extrusion
        filament_area = math.pi * (1.75 / 2)**2
        e_factor = (nozzle * layer_height) / filament_area
        current_e = 0.0
        
        for i in range(layers):
            z = zmin + i * layer_height
            # L'IA interroge sa formule mathématique (SDF) pour savoir ce qui est solide à cette hauteur Z
            solid_points = self.slice_layer_contours(z, resolution=nozzle)
            
            if not solid_points:
                continue
                
            gcode.append(f"; LAYER {i} Z={z:.2f}")
            gcode.append(f"G1 Z{z:.2f} F1500")
            
            # (Simplification extrême pour le prototype : on extrude point par point en ligne)
            # Un véritable algorithme trace des vecteurs (Marching Squares)
            solid_points.sort(key=lambda p: (p[0], p[1]))
            
            last_p = None
            for p in solid_points:
                if last_p is None or math.dist(last_p, p) > nozzle * 1.5:
                    gcode.append(f"G1 X{p[0]:.2f} Y{p[1]:.2f} F3000") # Déplacement à vide
                else:
                    dist = math.dist(last_p, p)
                    current_e += dist * e_factor
                    gcode.append(f"G1 X{p[0]:.2f} Y{p[1]:.2f} E{current_e:.4f} F1500") # Extrusion
                last_p = p
                
        gcode.append("G28 X Y\nM84")
        
        with open(filename, "w") as f:
            f.write("\n".join(gcode))
        print(f"[CSG Engine] Terminé ! Fichier prêt : {filename}")

if __name__ == "__main__":
    # Test d'imagination : L'IA "pense" à une boîte trouée par une sphère au centre
    # Boîte de 30x30x10 au centre (110, 110)
    base_box = Box(110, 110, 5, 30, 30, 10)
    # Sphère de rayon 10 au centre (creuse un cratère/trou)
    hole = Sphere(110, 110, 5, 10)
    
    # L'objet final est la boîte MOINS la sphère
    final_shape = Subtract(base_box, hole)
    
    # On instancie le cerveau CSG
    brain_slicer = CortexCSGSlicer(final_shape, bounding_box=(90, 130, 90, 130, 0, 10))
    brain_slicer.generate_gcode("output.gcode")
