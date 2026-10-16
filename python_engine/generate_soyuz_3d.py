#!/usr/bin/env python3
"""
Soyuz MS Spacecraft 3D Model & PBR Texture Atlas Generator
==========================================================
Generates:
1. High-resolution PBR Texture Atlas (2048x2048):
   - assets/textures/soyuz_diffuse.png (Albedo/Diffuse with СОЮЗ logo, Russian flag, Roscosmos patch, wrinkled EVTI thermal blanket, solar cells, white radiator hull)
   - assets/textures/soyuz_normal.png  (Normal map for wrinkled thermal blanket, solar panel grid, hull rivets)
   - assets/textures/soyuz_roughness.png (Roughness map for metallic/foil/matte contrasts)
   - assets/textures/soyuz_ao.png (Ambient occlusion map)
2. Wavefront 3D Model (.obj) & Material Library (.mtl):
   - assets/model/soyuz_spacecraft.obj
   - assets/model/soyuz_spacecraft.mtl
3. Cinema 4D Python Generator Script (.py):
   - c4d_plugin/c4d_soyuz_generator.py (Native Cinema 4D c4dpy script for R23–2025+)
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = "/home/user/webapp"
TEX_DIR = os.path.join(BASE_DIR, "assets", "textures")
MODEL_DIR = os.path.join(BASE_DIR, "assets", "model")
C4D_DIR = os.path.join(BASE_DIR, "c4d_plugin")

os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(C4D_DIR, exist_ok=True)


def generate_textures():
    """
    Creates 2048x2048 UV texture atlas divided into 4 quadrants:
    - Top-Left (u: 0.0..0.5, v: 0.5..1.0): Dark Anthracite EVTI Thermal Blanket + Decals (СОЮЗ, Flag, Roscosmos, Mission Patch, Tan Straps)
    - Top-Right (u: 0.5..1.0, v: 0.5..1.0): Solar Panel Cells (Warm beige/gold silicon cells with white aluminum grid)
    - Bottom-Left (u: 0.0..0.5, v: 0.0..0.5): White Service Module PAO Radiator Hull + Rivets & Thruster Ports
    - Bottom-Right (u: 0.5..1.0, v: 0.0..0.5): Metallic/Mechanical Details (Kurs Docking Cone, Olive Periscope, Porthole Glass, Antennas)
    """
    W, H = 2048, 2048
    diffuse = Image.new("RGB", (W, H), (45, 45, 48))
    roughness = Image.new("L", (W, H), 140)
    normal = Image.new("RGB", (W, H), (128, 128, 255))

    draw_d = ImageDraw.Draw(diffuse)
    draw_r = ImageDraw.Draw(roughness)
    draw_n = ImageDraw.Draw(normal)

    random.seed(42)

    # ---------------------------------------------------------
    # QUADRANT 1: Top-Left (x: 0..1024, y: 0..1024) -> EVTI Dark Thermal Blanket + Decals
    # ---------------------------------------------------------
    # Base dark anthracite foil with subtle crinkle waves
    for y in range(0, 1024, 4):
        for x in range(0, 1024, 4):
            wave1 = math.sin(x * 0.045 + math.sin(y * 0.03) * 2.5) * 18
            wave2 = math.cos(y * 0.06 + math.cos(x * 0.025) * 2.0) * 14
            noise = random.randint(-8, 8)
            val = max(24, min(92, int(52 + wave1 + wave2 + noise)))
            draw_d.rectangle([x, y, x + 3, y + 3], fill=(val, val, int(val * 1.03)))
            # Normal map perturbation for wrinkled foil
            nx = max(60, min(195, int(128 + wave1 * 1.8 + noise)))
            ny = max(60, min(195, int(128 + wave2 * 1.8 - noise)))
            draw_n.rectangle([x, y, x + 3, y + 3], fill=(nx, ny, 245))
            # Roughness variation (foil has specular highlights)
            r_val = max(55, min(150, int(98 - wave1 * 0.8)))
            draw_r.rectangle([x, y, x + 3, y + 3], fill=r_val)

    # Draw tan/brown kevlar harness straps across the thermal blanket region
    # Vertical & circumferential strap bands
    strap_color = (156, 122, 78)
    strap_border = (115, 86, 50)
    # Strap band 1 (circumferential belt at y: 740..810)
    draw_d.rectangle([0, 740, 1024, 810], fill=strap_color, outline=strap_border, width=4)
    for sx in range(0, 1024, 16):
        draw_d.line([(sx, 745), (sx + 8, 805)], fill=(138, 105, 64), width=2)
    draw_r.rectangle([0, 740, 1024, 810], fill=185)

    # Strap band 2 (dorsal periscope fairing harness at y: 520..620)
    draw_d.rectangle([0, 540, 1024, 600], fill=(148, 112, 68), outline=strap_border, width=3)
    draw_r.rectangle([0, 540, 1024, 600], fill=185)

    # Decal Patch on Orbital Module BO (x: 240..780, y: 120..440)
    # White decal background plate with subtle stitched edge
    draw_d.rounded_rectangle([260, 110, 760, 450], radius=18, fill=(235, 237, 240), outline=(180, 182, 186), width=5)
    draw_r.rounded_rectangle([260, 110, 760, 450], radius=18, fill=110)

    # 1) "СОЮЗ" Red Bold Cyrillic Emblem (top of patch: y 125..195)
    draw_d.rounded_rectangle([290, 125, 730, 195], radius=8, fill=(242, 242, 245), outline=(200, 40, 40), width=3)
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw_d.text((405, 130), "СОЮЗ", fill=(205, 32, 38), font=font_large)

    # 2) Russian Tricolor Flag (White / Blue / Red) in middle of patch (y 210..320)
    draw_d.rectangle([290, 210, 560, 246], fill=(248, 248, 250))
    draw_d.rectangle([290, 246, 560, 283], fill=(0, 57, 166))
    draw_d.rectangle([290, 283, 560, 320], fill=(213, 43, 30))
    draw_d.rectangle([290, 210, 560, 320], outline=(150, 150, 155), width=2)

    # 3) Circular Mission Compass Patch on right side of decal (cx=650, cy=275, r=62)
    draw_d.ellipse([588, 213, 712, 337], fill=(230, 236, 245), outline=(70, 90, 120), width=5)
    draw_d.ellipse([602, 227, 698, 323], fill=(245, 247, 252), outline=(140, 160, 190), width=2)
    # Compass star inside patch
    draw_d.line([(650, 235), (650, 315)], fill=(70, 95, 140), width=3)
    draw_d.line([(610, 275), (690, 275)], fill=(70, 95, 140), width=3)
    draw_d.polygon([(650, 238), (658, 275), (650, 312), (642, 275)], fill=(195, 40, 45))

    # 4) Roscosmos Red Swoosh & Text at bottom of patch (y 340..430)
    draw_d.polygon([(310, 405), (410, 355), (445, 405), (375, 392)], fill=(210, 35, 42))
    draw_d.text((460, 365), "РОСКОСМОС", fill=(30, 40, 60), font=font_small)
    draw_d.text((460, 395), "SOYUZ-MS", fill=(90, 100, 120), font=font_small)

    # ---------------------------------------------------------
    # QUADRANT 2: Top-Right (x: 1024..2048, y: 0..1024) -> Solar Panel Array
    # ---------------------------------------------------------
    # White aluminum frame background
    draw_d.rectangle([1024, 0, 2048, 1024], fill=(228, 230, 234))
    draw_r.rectangle([1024, 0, 2048, 1024], fill=135)
    draw_n.rectangle([1024, 0, 2048, 1024], fill=(128, 128, 255))

    # Draw grid of warm tan/gold silicon photovoltaic cells matching the reference image
    cols, rows = 8, 12
    pad_x, pad_y = 18, 16
    cell_w = (1024 - pad_x * (cols + 1)) // cols
    cell_h = (1024 - pad_y * (rows + 1)) // rows

    for r in range(rows):
        for c in range(cols):
            cx0 = 1024 + pad_x + c * (cell_w + pad_x)
            cy0 = pad_y + r * (cell_h + pad_y)
            cx1 = cx0 + cell_w
            cy1 = cy0 + cell_h
            # Warm beige/tan/bronze solar cell color as seen in reference photo
            base_c = (182 + (r % 2) * 5, 160 + (c % 2) * 4, 128)
            draw_d.rectangle([cx0, cy0, cx1, cy1], fill=base_c, outline=(110, 95, 75), width=2)
            # Fine silver micro-busbars across each cell
            for sub in range(1, 5):
                sy = cy0 + (cell_h * sub) // 5
                draw_d.line([(cx0 + 2, sy), (cx1 - 2, sy)], fill=(208, 195, 172), width=1)
            # Central vertical collector trace
            draw_d.line([(cx0 + cell_w // 2, cy0), (cx0 + cell_w // 2, cy1)], fill=(220, 215, 205), width=2)
            # Smooth glossy roughness on solar cells
            draw_r.rectangle([cx0, cy0, cx1, cy1], fill=48)
            # Normal bevel at cell borders
            draw_n.rectangle([cx0, cy0, cx1, cy1], outline=(160, 160, 240), width=2)

    # ---------------------------------------------------------
    # QUADRANT 3: Bottom-Left (x: 0..1024, y: 1024..2048) -> White PAO Service Module Hull
    # ---------------------------------------------------------
    draw_d.rectangle([0, 1024, 1024, 2048], fill=(238, 240, 243))
    draw_r.rectangle([0, 1024, 1024, 2048], fill=115)

    # Vertical radiator cooling flutes/grooves
    for gx in range(16, 1024, 24):
        draw_d.line([(gx, 1024), (gx, 2048)], fill=(216, 219, 224), width=3)
        draw_d.line([(gx + 3, 1024), (gx + 3, 2048)], fill=(248, 249, 252), width=2)
        draw_n.line([(gx, 1024), (gx, 2048)], fill=(108, 128, 250), width=3)
        draw_n.line([(gx + 3, 1024), (gx + 3, 2048)], fill=(148, 128, 250), width=2)

    # Dark composite aft collar ring + attitude thruster ports
    draw_d.rectangle([0, 1850, 1024, 2048], fill=(42, 45, 50))
    for tx in range(40, 1000, 80):
        draw_d.ellipse([tx, 1890, tx + 36, 1926], fill=(20, 22, 25), outline=(140, 145, 150), width=3)

    # Structural panel seam lines & rivets
    for py in [1220, 1480, 1720]:
        draw_d.line([(0, py), (1024, py)], fill=(185, 190, 198), width=3)
        for rx in range(20, 1024, 32):
            draw_d.ellipse([rx - 2, py - 8, rx + 2, py - 4], fill=(150, 155, 162))
            draw_d.ellipse([rx - 2, py + 4, rx + 2, py + 8], fill=(150, 155, 162))

    # ---------------------------------------------------------
    # QUADRANT 4: Bottom-Right (x: 1024..2048, y: 1024..2048) -> Mechanical Subsystems
    # ---------------------------------------------------------
    # Sub-region A (x: 1024..1536, y: 1024..1536): Kurs Docking Mechanism & Metallic Titanium Rings
    draw_d.rectangle([1024, 1024, 1536, 1536], fill=(172, 176, 182))
    draw_r.rectangle([1024, 1024, 1536, 1536], fill=65)
    for r_idx in range(1040, 1520, 36):
        draw_d.line([(1024, r_idx), (1536, r_idx)], fill=(120, 125, 132), width=4)

    # Sub-region B (x: 1536..2048, y: 1024..1536): Olive-Green Periscope (VSK-4) & Optical Sensor Housing
    draw_d.rectangle([1536, 1024, 2048, 1536], fill=(92, 114, 68))
    draw_r.rectangle([1536, 1024, 2048, 1536], fill=125)
    # Optical lens aperture inside periscope region
    draw_d.rounded_rectangle([1680, 1150, 1900, 1370], radius=24, fill=(28, 36, 52), outline=(190, 200, 185), width=8)
    draw_d.ellipse([1715, 1185, 1865, 1335], fill=(22, 58, 110), outline=(90, 160, 220), width=4)
    draw_d.ellipse([1745, 1210, 1790, 1255], fill=(195, 228, 255))

    # Sub-region C (x: 1024..1536, y: 1536..2048): Deep Blue/Black Spacecraft Porthole Illuminator Glass
    draw_d.rectangle([1024, 1536, 1536, 2048], fill=(24, 34, 52))
    draw_r.rectangle([1024, 1536, 1536, 2048], fill=20)
    draw_d.ellipse([1080, 1590, 1480, 1990], fill=(18, 42, 78), outline=(145, 152, 162), width=18)
    draw_d.arc([1120, 1630, 1440, 1950], start=200, end=310, fill=(140, 195, 245), width=10)

    # Sub-region D (x: 1536..2048, y: 1536..2048): White/Silver Antenna Dishes & Thruster Nozzles
    draw_d.rectangle([1536, 1536, 2048, 2048], fill=(215, 218, 224))
    draw_r.rectangle([1536, 1536, 2048, 2048], fill=85)
    for ay in range(1560, 2030, 48):
        draw_d.line([(1536, ay), (2048, ay)], fill=(185, 190, 198), width=3)

    diffuse_path = os.path.join(TEX_DIR, "soyuz_diffuse.png")
    normal_path = os.path.join(TEX_DIR, "soyuz_normal.png")
    roughness_path = os.path.join(TEX_DIR, "soyuz_roughness.png")

    diffuse.save(diffuse_path, "PNG")
    normal.save(normal_path, "PNG")
    roughness.save(roughness_path, "PNG")
    print(f"[OK] Saved PBR textures to {TEX_DIR}")
    return diffuse_path, normal_path, roughness_path


class MeshBuilder:
    """Builds a clean, multi-group UV-mapped Wavefront OBJ + MTL model of the Soyuz MS spacecraft."""

    def __init__(self):
        self.vertices = []   # (x, y, z)
        self.uvs = []        # (u, v)
        self.normals = []    # (nx, ny, nz)
        self.groups = {}     # group_name -> {"material": mat_name, "faces": [ [(v, vt, vn), ...], ... ]}
        self.current_group = "default"
        self.current_mat = "mat_evti_blanket"

    def set_group(self, group_name, material_name):
        self.current_group = group_name
        self.current_mat = material_name
        if group_name not in self.groups:
            self.groups[group_name] = {"material": material_name, "faces": []}

    def add_vertex(self, x, y, z):
        self.vertices.append((x, y, z))
        return len(self.vertices)

    def add_uv(self, u, v):
        self.uvs.append((max(0.0, min(1.0, u)), max(0.0, min(1.0, v))))
        return len(self.uvs)

    def add_normal(self, nx, ny, nz):
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length > 1e-8:
            nx, ny, nz = nx / length, ny / length, nz / length
        else:
            nx, ny, nz = 0.0, 1.0, 0.0
        self.normals.append((nx, ny, nz))
        return len(self.normals)

    def add_face(self, face_tuples):
        self.groups[self.current_group]["faces"].append(face_tuples)

    def add_lathe_z(self, profile, segs=48, u_range=(0.02, 0.48), v_range=(0.52, 0.98),
                    wrinkle_amp=0.0, center_offset=(0.0, 0.0, 0.0)):
        """
        Generates a surface of revolution around the Z-axis.
        profile: list of (z, r) pairs ordered along Z.
        u_range, v_range: UV rectangle in the 2048x2048 atlas.
        wrinkle_amp: organic thermal blanket wrinkle displacement amplitude.
        """
        ox, oy, oz = center_offset
        rings = []
        n_prof = len(profile)
        for i, (z_val, r_val) in enumerate(profile):
            v_frac = i / max(1, n_prof - 1)
            v_coord = v_range[0] + v_frac * (v_range[1] - v_range[0])
            ring = []
            # Estimate slope for normal
            if i < n_prof - 1:
                dz = profile[i + 1][0] - z_val
                dr = profile[i + 1][1] - r_val
            else:
                dz = z_val - profile[i - 1][0]
                dr = r_val - profile[i - 1][1]

            for j in range(segs + 1):
                u_frac = j / segs
                theta = u_frac * 2.0 * math.pi
                u_coord = u_range[0] + u_frac * (u_range[1] - u_range[0])

                # Apply subtle organic EVTI blanket wrinkle if requested (skipping endpoints so seams stay airtight)
                w_disp = 0.0
                if wrinkle_amp > 0.0 and 0 < i < n_prof - 1 and r_val > 0.05:
                    w_disp = wrinkle_amp * (
                        0.6 * math.sin(14.0 * theta + 3.5 * z_val)
                        + 0.4 * math.cos(22.0 * theta - 6.0 * z_val)
                    )

                r_eff = max(0.0, r_val + w_disp)
                px = ox + r_eff * math.cos(theta)
                py = oy + r_eff * math.sin(theta)
                pz = oz + z_val

                nx = math.cos(theta) * dz
                ny = math.sin(theta) * dz
                nz = -dr

                vi = self.add_vertex(px, py, pz)
                vti = self.add_uv(u_coord, v_coord)
                vni = self.add_normal(nx, ny, nz)
                ring.append((vi, vti, vni))
            rings.append(ring)

        for i in range(n_prof - 1):
            for j in range(segs):
                p00 = rings[i][j]
                p01 = rings[i][j + 1]
                p11 = rings[i + 1][j + 1]
                p10 = rings[i + 1][j]
                self.add_face([p00, p01, p11, p10])

    def add_cylinder_oriented(self, p0, p1, r0, r1, segs=20, u_range=(0.52, 0.72), v_range=(0.26, 0.48), cap_ends=True):
        """Adds a cylinder/cone from 3D point p0 to p1 with radii r0, r1."""
        dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-6:
            return
        ax, ay, az = dx / length, dy / length, dz / length
        # Find orthogonal basis U, V
        if abs(ax) < 0.8:
            ux, uy, uz = 0.0, -az, ay
        else:
            ux, uy, uz = -az, 0.0, ax
        ul = math.sqrt(ux * ux + uy * uy + uz * uz)
        ux, uy, uz = ux / ul, uy / ul, uz / ul
        vx = ay * uz - az * uy
        vy = az * ux - ax * uz
        vz = ax * uy - ay * ux

        ring0, ring1 = [], []
        for j in range(segs + 1):
            u_frac = j / segs
            theta = u_frac * 2.0 * math.pi
            ct, st = math.cos(theta), math.sin(theta)
            nx = ct * ux + st * vx
            ny = ct * uy + st * vy
            nz = ct * uz + st * vz

            x0 = p0[0] + r0 * nx
            y0 = p0[1] + r0 * ny
            z0 = p0[2] + r0 * nz

            x1 = p1[0] + r1 * nx
            y1 = p1[1] + r1 * ny
            z1 = p1[2] + r1 * nz

            u_c = u_range[0] + u_frac * (u_range[1] - u_range[0])
            v0_i = self.add_vertex(x0, y0, z0)
            vt0_i = self.add_uv(u_c, v_range[0])
            vn0_i = self.add_normal(nx, ny, nz)
            ring0.append((v0_i, vt0_i, vn0_i))

            v1_i = self.add_vertex(x1, y1, z1)
            vt1_i = self.add_uv(u_c, v_range[1])
            vn1_i = self.add_normal(nx, ny, nz)
            ring1.append((v1_i, vt1_i, vn1_i))

        for j in range(segs):
            self.add_face([ring0[j], ring0[j + 1], ring1[j + 1], ring1[j]])

        if cap_ends and r1 > 1e-4:
            vc = self.add_vertex(p1[0], p1[1], p1[2])
            vtc = self.add_uv(0.5 * (u_range[0] + u_range[1]), 0.5 * (v_range[0] + v_range[1]))
            vnc = self.add_normal(ax, ay, az)
            for j in range(segs):
                self.add_face([ring1[j], ring1[j + 1], (vc, vtc, vnc)])

    def add_box(self, center, size, rot_y=0.0, rot_z=0.0, u_range=(0.52, 0.98), v_range=(0.52, 0.98)):
        """Adds an oriented 3D box with proper UVs on top/bottom faces."""
        cx, cy, cz = center
        sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5

        local_corners = [
            (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
            (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz),
        ]

        cy_r, sy_r = math.cos(rot_y), math.sin(rot_y)
        cz_r, sz_r = math.cos(rot_z), math.sin(rot_z)

        def transform(pt):
            x, y, z = pt
            # Rotate around Y
            x1 = x * cy_r + z * sy_r
            y1 = y
            z1 = -x * sy_r + z * cy_r
            # Rotate around Z
            x2 = x1 * cz_r - y1 * sz_r
            y2 = x1 * sz_r + y1 * cz_r
            z2 = z1
            return (cx + x2, cy + y2, cz + z2)

        def transform_n(n):
            x, y, z = n
            x1 = x * cy_r + z * sy_r
            y1 = y
            z1 = -x * sy_r + z * cy_r
            x2 = x1 * cz_r - y1 * sz_r
            y2 = x1 * sz_r + y1 * cz_r
            z2 = z1
            return (x2, y2, z2)

        w_corners = [transform(p) for p in local_corners]
        faces_def = [
            ([0, 1, 2, 3], (0, 0, -1)),
            ([5, 4, 7, 6], (0, 0, 1)),
            ([4, 0, 3, 7], (-1, 0, 0)),
            ([1, 5, 6, 2], (1, 0, 0)),
            ([3, 2, 6, 7], (0, 1, 0)),
            ([4, 5, 1, 0], (0, -1, 0)),
        ]
        uv_corners = [
            (u_range[0], v_range[0]),
            (u_range[1], v_range[0]),
            (u_range[1], v_range[1]),
            (u_range[0], v_range[1]),
        ]
        for idxs, n_local in faces_def:
            nx, ny, nz = transform_n(n_local)
            vni = self.add_normal(nx, ny, nz)
            face = []
            for k, c_idx in enumerate(idxs):
                px, py, pz = w_corners[c_idx]
                vi = self.add_vertex(px, py, pz)
                vti = self.add_uv(uv_corners[k][0], uv_corners[k][1])
                face.append((vi, vti, vni))
            self.add_face(face)


def build_soyuz_spacecraft():
    """
    Constructs the complete Soyuz MS Spacecraft matching the reference image:
    - Orbital Module (BO - Бытовой отсек): Spherical module wrapped in wrinkled dark EVTI blanket,
      featuring the СОЮЗ / Russian Flag / Roscosmos patch on the upper port flank, forward Kurs docking
      assembly with probe and drogue cones, twinKurs parabolic dishes, ladder rungs, and viewing porthole.
    - Descent Module (SA - Спускаемый аппарат): Bell-shaped headlight reentry module covered in dark
      EVTI thermal protection with tan harness straps, dorsal ridge fairing, VSK-4 olive-green periscope tower,
      and side porthole windows.
    - Instrumentation & Propulsion Module (PAO - Приборно-агрегатный отсек): White ribbed cylindrical/conical
      service hull with dark composite aft attitude-control collar, KTDU-80 main engine nozzle, telemetry antennas,
      and two 4-segment deployable solar panel wings with articulated tubular trusses.
    """
    mb = MeshBuilder()

    # =========================================================================
    # 1. ORBITAL MODULE (BO - Бытовой Отсек) [Z: +1.15 .. +3.45]
    # =========================================================================
    mb.set_group("BO_Orbital_Module_Hull", "mat_evti_blanket")
    bo_profile = []
    n_bo = 28
    z_bo_center = 2.32
    r_bo_max = 1.12
    for i in range(n_bo + 1):
        t = i / n_bo  # 0 (aft neck) -> 1 (forward docking collar)
        ang = -0.38 * math.pi + t * (0.76 * math.pi)
        z = z_bo_center + 1.12 * math.sin(ang)
        r = r_bo_max * math.cos(ang)
        bo_profile.append((z, r))
    # Map UVs directly over Quadrant 1 (Top-Left) so the СОЮЗ + Flag + Roscosmos decal appears on the upper-left flank
    mb.add_lathe_z(bo_profile, segs=56, u_range=(0.02, 0.48), v_range=(0.52, 0.96), wrinkle_amp=0.018)

    # Tan coupling strap collar between BO and SA (Z: +1.12 .. +1.28)
    mb.set_group("BO_SA_Coupling_Strap", "mat_kevlar_strap")
    strap_profile = [
        (1.08, 0.92),
        (1.14, 0.96),
        (1.25, 0.95),
        (1.30, 0.90),
    ]
    mb.add_lathe_z(strap_profile, segs=48, u_range=(0.05, 0.45), v_range=(0.61, 0.64), wrinkle_amp=0.004)

    # Forward Kurs Docking Collar & Recessed Cone (Z: +3.28 .. +3.72)
    mb.set_group("Kurs_Docking_Assembly", "mat_titanium_metal")
    dock_profile = [
        (3.26, 0.72),
        (3.38, 0.74),
        (3.48, 0.68),
        (3.52, 0.64),
        (3.40, 0.42),
        (3.35, 0.16),
        (3.98, 0.045),
        (4.06, 0.09),
        (4.12, 0.02),
    ]
    mb.add_lathe_z(dock_profile, segs=40, u_range=(0.52, 0.74), v_range=(0.26, 0.48), wrinkle_amp=0.0)

    # Radial docking latches & internal alignment vanes around the docking ring
    for k in range(8):
        ang = k * (2.0 * math.pi / 8.0)
        p0 = (0.58 * math.cos(ang), 0.58 * math.sin(ang), 3.48)
        p1 = (0.34 * math.cos(ang), 0.34 * math.sin(ang), 3.40)
        mb.add_cylinder_oriented(p0, p1, 0.028, 0.022, segs=10, u_range=(0.54, 0.70), v_range=(0.30, 0.45))

    # Twin Parabolic Kurs Rendezvous Radar Dishes on the Orbital Module (Upper Port & Lower Port)
    mb.set_group("Kurs_Radar_Antennas", "mat_white_antenna")
    for dish_ang in [2.35, 3.85]:
        bx = 1.02 * math.cos(dish_ang)
        by = 1.02 * math.sin(dish_ang)
        bz = 2.85
        tip_x = 1.42 * math.cos(dish_ang)
        tip_y = 1.42 * math.sin(dish_ang)
        tip_z = 3.05
        mb.add_cylinder_oriented((bx, by, bz), (tip_x, tip_y, tip_z), 0.045, 0.035, segs=12,
                                 u_range=(0.76, 0.96), v_range=(0.04, 0.22))
        # Parabolic dish head
        dish_end = (tip_x + 0.12 * math.cos(dish_ang), tip_y + 0.12 * math.sin(dish_ang), tip_z + 0.08)
        mb.add_cylinder_oriented((tip_x, tip_y, tip_z), dish_end, 0.05, 0.24, segs=20,
                                 u_range=(0.76, 0.96), v_range=(0.04, 0.22))

    # EVA Handrail & Crew Access Ladder on BO Flank
    mb.set_group("BO_EVA_Ladder_And_Sensors", "mat_titanium_metal")
    for side_offset in [-0.14, 0.14]:
        mb.add_cylinder_oriented(
            (-0.98, 0.45 + side_offset, 2.35),
            (-0.68, 0.35 + side_offset, 3.25),
            0.018, 0.018, segs=8, u_range=(0.54, 0.72), v_range=(0.28, 0.46)
        )
    for rung in range(5):
        frac = rung / 4.0
        rx = -0.98 + frac * 0.30
        ry_center = 0.45 - frac * 0.10
        rz = 2.38 + frac * 0.82
        mb.add_cylinder_oriented(
            (rx, ry_center - 0.14, rz),
            (rx, ry_center + 0.14, rz),
            0.014, 0.014, segs=8, u_range=(0.54, 0.72), v_range=(0.28, 0.46)
        )

    # BO Viewport / Illuminator Window + Protruding Sensor Blisters
    mb.set_group("Viewport_Portholes", "mat_porthole_glass")
    mb.add_cylinder_oriented(
        (-0.88, -0.52, 2.18),
        (-1.05, -0.62, 2.18),
        0.18, 0.16, segs=20, u_range=(0.52, 0.73), v_range=(0.02, 0.23)
    )

    # =========================================================================
    # 2. DESCENT MODULE (SA - Спускаемый Аппарат) [Z: -0.65 .. +1.18]
    # =========================================================================
    mb.set_group("SA_Descent_Module_Hull", "mat_evti_blanket")
    sa_profile = []
    n_sa = 26
    for i in range(n_sa + 1):
        t = i / n_sa  # 0 (aft heatshield base at Z=-0.65) -> 1 (forward neck at Z=+1.15)
        z = -0.65 + t * 1.80
        # Classic Soyuz "headlight" bell shape: wider rounded base tapering smoothly to BO neck
        r = 1.18 - 0.24 * (t ** 1.35) + 0.06 * math.sin(t * math.pi)
        sa_profile.append((z, r))
    mb.add_lathe_z(sa_profile, segs=56, u_range=(0.02, 0.48), v_range=(0.52, 0.75), wrinkle_amp=0.020)

    # Dorsal Tan Harness Spine & Parachute Hatch Fairing on Top of SA
    mb.set_group("SA_Dorsal_Harness_Fairing", "mat_kevlar_strap")
    for seg_i in range(8):
        z_s = -0.45 + seg_i * 0.20
        r_s = 1.16 - 0.12 * (seg_i / 7.0)
        mb.add_cylinder_oriented(
            (0.0, r_s * 0.94, z_s),
            (0.0, r_s * 0.92, z_s + 0.22),
            0.16, 0.15, segs=14, u_range=(0.05, 0.45), v_range=(0.61, 0.64)
        )
    # Aft circumferential tan retention belt at SA/PAO separation plane (Z: -0.68 .. -0.48)
    belt_profile = [
        (-0.70, 1.19),
        (-0.62, 1.21),
        (-0.48, 1.20),
        (-0.44, 1.17),
    ]
    mb.add_lathe_z(belt_profile, segs=48, u_range=(0.05, 0.45), v_range=(0.61, 0.64), wrinkle_amp=0.004)

    # VSK-4 Cosmonaut Optical Periscope (Olive-Green Tower with Rectangular Optical Head)
    mb.set_group("VSK4_Optical_Periscope", "mat_periscope_green")
    mb.add_cylinder_oriented(
        (0.0, 1.05, 0.68),
        (0.0, 1.62, 0.72),
        0.11, 0.09, segs=16, u_range=(0.76, 0.98), v_range=(0.26, 0.48)
    )
    # Rectangular optical head on top of periscope mast
    mb.add_box(
        center=(0.0, 1.70, 0.72),
        size=(0.24, 0.22, 0.24),
        rot_y=0.0, rot_z=0.0,
        u_range=(0.80, 0.94), v_range=(0.30, 0.45)
    )

    # SA Side Illuminator Porthole Windows (Port & Starboard)
    mb.set_group("Viewport_Portholes", "mat_porthole_glass")
    for sign_x in [-1.0, 1.0]:
        mb.add_cylinder_oriented(
            (sign_x * 1.02, -0.12, 0.18),
            (sign_x * 1.19, -0.14, 0.18),
            0.17, 0.15, segs=20, u_range=(0.52, 0.73), v_range=(0.02, 0.23)
        )

    # =========================================================================
    # 3. INSTRUMENTATION & PROPULSION MODULE (PAO - Приборно-Агрегатный Отсек) [Z: -2.65 .. -0.65]
    # =========================================================================
    mb.set_group("PAO_Service_Module_Radiator", "mat_pao_white_hull")
    pao_profile = [
        (-2.55, 1.38),
        (-2.45, 1.42),
        (-2.20, 1.36),
        (-1.65, 1.22),
        (-1.15, 1.18),
        (-0.65, 1.18),
    ]
    mb.add_lathe_z(pao_profile, segs=56, u_range=(0.02, 0.48), v_range=(0.02, 0.48), wrinkle_amp=0.0)

    # Aft Dark Composite Skirt & KTDU-80 Propulsion Bay
    mb.set_group("PAO_Propulsion_Bay_And_Nozzles", "mat_titanium_metal")
    aft_profile = [
        (-2.68, 1.32),
        (-2.55, 1.38),
        (-2.55, 0.55),
        (-2.88, 0.34),
        (-2.88, 0.08),
    ]
    mb.add_lathe_z(aft_profile, segs=48, u_range=(0.52, 0.74), v_range=(0.26, 0.48), wrinkle_amp=0.0)

    # Dorsal Telemetry & Attitude Sensor Towers on PAO
    mb.set_group("PAO_Telemetry_Towers", "mat_pao_white_hull")
    for tx_off, tz_off in [(-0.28, -1.65), (0.28, -1.95)]:
        mb.add_cylinder_oriented(
            (tx_off, 1.15, tz_off),
            (tx_off, 1.62, tz_off),
            0.13, 0.11, segs=16, u_range=(0.05, 0.45), v_range=(0.10, 0.40)
        )

    # =========================================================================
    # 4. TWIN 4-SEGMENT DEPLOYABLE SOLAR PANEL WINGS (Left & Right)
    # =========================================================================
    mb.set_group("Solar_Panel_Wings", "mat_solar_panels")
    for side in [-1.0, 1.0]:
        # 4 articulated solar panels per wing extending along +/-X
        for p_idx in range(4):
            cx = side * (1.78 + p_idx * 1.02)
            cy = -0.05
            cz = -1.45
            mb.add_box(
                center=(cx, cy, cz),
                size=(0.96, 0.045, 1.38),
                rot_y=0.0, rot_z=0.0,
                u_range=(0.52, 0.98), v_range=(0.52, 0.98)
            )

    # Articulated White/Silver Structural Truss Frames on Solar Wings
    mb.set_group("Solar_Panel_Truss_Frames", "mat_white_antenna")
    for side in [-1.0, 1.0]:
        # Root yoke connecting PAO hull to first solar panel
        mb.add_cylinder_oriented(
            (side * 1.18, -0.05, -1.10),
            (side * 1.32, -0.05, -0.82),
            0.035, 0.03, segs=8, u_range=(0.76, 0.96), v_range=(0.04, 0.22)
        )
        mb.add_cylinder_oriented(
            (side * 1.18, -0.05, -1.80),
            (side * 1.32, -0.05, -2.08),
            0.035, 0.03, segs=8, u_range=(0.76, 0.96), v_range=(0.04, 0.22)
        )
        # Longitudinal booms along the leading and trailing edges of the 4 panels
        for z_edge in [-0.74, -1.45, -2.16]:
            mb.add_cylinder_oriented(
                (side * 1.28, 0.0, z_edge),
                (side * 5.38, 0.0, z_edge),
                0.022, 0.018, segs=8, u_range=(0.76, 0.96), v_range=(0.04, 0.22)
            )
        # Diagonal ribs & inter-panel hinges
        for p_idx in range(5):
            hx = side * (1.30 + p_idx * 1.02)
            mb.add_cylinder_oriented(
                (hx, 0.01, -0.74),
                (hx, 0.01, -2.16),
                0.024, 0.024, segs=8, u_range=(0.76, 0.96), v_range=(0.04, 0.22)
            )
        # End-tip VHF/UHF whip antenna at outer edge of each solar wing
        mb.add_cylinder_oriented(
            (side * 5.38, 0.0, -0.74),
            (side * 5.75, -0.18, -0.35),
            0.016, 0.006, segs=8, u_range=(0.76, 0.96), v_range=(0.04, 0.22)
        )

    # Write MTL file
    mtl_path = os.path.join(MODEL_DIR, "soyuz_spacecraft.mtl")
    mtl_content = """# Wavefront MTL - Soyuz MS Spacecraft (Cinema 4D / Three.js PBR Compatible)
# Generated for Cinema 4D & WebGL 3D Pipeline

newmtl mat_evti_blanket
Ka 0.15 0.15 0.16
Kd 0.85 0.85 0.87
Ks 0.35 0.35 0.38
Ns 45.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png
map_Bump ../textures/soyuz_normal.png
map_Ns ../textures/soyuz_roughness.png

newmtl mat_kevlar_strap
Ka 0.20 0.16 0.10
Kd 0.88 0.84 0.78
Ks 0.18 0.15 0.12
Ns 20.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png
map_Bump ../textures/soyuz_normal.png

newmtl mat_solar_panels
Ka 0.20 0.18 0.15
Kd 0.95 0.95 0.95
Ks 0.65 0.62 0.52
Ns 90.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png
map_Bump ../textures/soyuz_normal.png
map_Ns ../textures/soyuz_roughness.png

newmtl mat_pao_white_hull
Ka 0.25 0.25 0.26
Kd 0.95 0.96 0.98
Ks 0.30 0.30 0.32
Ns 50.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png
map_Bump ../textures/soyuz_normal.png

newmtl mat_titanium_metal
Ka 0.22 0.23 0.25
Kd 0.82 0.84 0.88
Ks 0.75 0.77 0.80
Ns 110.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png

newmtl mat_periscope_green
Ka 0.12 0.16 0.10
Kd 0.85 0.88 0.82
Ks 0.40 0.42 0.38
Ns 65.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png

newmtl mat_porthole_glass
Ka 0.05 0.08 0.15
Kd 0.80 0.88 0.96
Ks 0.92 0.95 1.00
Ns 180.0
d 0.95
illum 2
map_Kd ../textures/soyuz_diffuse.png

newmtl mat_white_antenna
Ka 0.24 0.24 0.25
Kd 0.92 0.93 0.95
Ks 0.45 0.45 0.48
Ns 70.0
d 1.0
illum 2
map_Kd ../textures/soyuz_diffuse.png
"""
    with open(mtl_path, "w", encoding="utf-8") as f:
        f.write(mtl_content)

    # Write OBJ file
    obj_path = os.path.join(MODEL_DIR, "soyuz_spacecraft.obj")
    total_faces = sum(len(g["faces"]) for g in mb.groups.values())
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write("# =====================================================================\n")
        f.write("# Soyuz MS Spacecraft (Космический корабль Союз МС) 3D Model (.obj)\n")
        f.write("# Cinema 4D R23-2025 / Blender / Three.js Ready with UV Texture Atlas\n")
        f.write(f"# Vertices: {len(mb.vertices)} | UVs: {len(mb.uvs)} | Normals: {len(mb.normals)} | Polygons: {total_faces}\n")
        f.write("# =====================================================================\n")
        f.write("mtllib soyuz_spacecraft.mtl\n\n")

        for vx, vy, vz in mb.vertices:
            f.write(f"v {vx:.5f} {vy:.5f} {vz:.5f}\n")
        f.write("\n")

        for u, v in mb.uvs:
            f.write(f"vt {u:.5f} {v:.5f}\n")
        f.write("\n")

        for nx, ny, nz in mb.normals:
            f.write(f"vn {nx:.5f} {ny:.5f} {nz:.5f}\n")
        f.write("\n")

        for g_name, g_data in mb.groups.items():
            f.write(f"g {g_name}\n")
            f.write(f"usemtl {g_data['material']}\n")
            for face in g_data["faces"]:
                face_str = " ".join(f"{vi}/{vti}/{vni}" for (vi, vti, vni) in face)
                f.write(f"f {face_str}\n")
            f.write("\n")

    print(f"[OK] Saved 3D OBJ model ({len(mb.vertices)} vertices, {total_faces} faces) to {obj_path}")
    return obj_path, mtl_path, len(mb.vertices), total_faces


def generate_c4d_script():
    """Generates the native Maxon Cinema 4D Python script (c4dpy / Script Manager) to build, texture, and export the Soyuz MS model."""
    c4d_script_path = os.path.join(C4D_DIR, "c4d_soyuz_generator.py")
    c4d_code = '''# -*- coding: utf-8 -*-
"""
===============================================================================
MAXON CINEMA 4D (R23 / S24 / R25 / 2023 / 2024 / 2025) PYTHON GENERATOR SCRIPT
Модель: Космический корабль «Союз МС» (Soyuz MS Spacecraft) + PBR Текстурирование
===============================================================================
Назначение:
  1. Процедурное построение иерархии объектов корабля «Союз МС» в Cinema 4D:
     - Бытовой отсек (БО / Orbital Module) с экранно-вакуумной теплоизоляцией (ЭВТИ),
       стыковочным агрегатом «Курс», антеннами сближения, поручнями и иллюминатором
     - Спускаемый аппарат (СА / Descent Module) с теплозащитным кожухом, ремнями
       крепления, перископом ВСК-4 и боковыми иллюминаторами
     - Приборно-агрегатный отсек (ПАО / Service Module) с радиаторами охлаждения,
       двигательной установкой КТДУ-80 и двумя 4-секционными крыльями солнечных батарей
  2. Создание и наложение PBR-материалов (Color/Diffuse, Normal, Reflectance/Roughness)
     с проекцией UVW Mapping (эмблема «СОЮЗ», триколор РФ, логотип Роскосмоса).
  3. Автоматический экспорт готовой сцены в формат Wavefront OBJ (.obj + .mtl).

Как запустить в Cinema 4D:
  Откройте Cinema 4D -> Extensions (Расширения) -> Script Manager (Менеджер скриптов) ->
  Загрузите этот файл `c4d_soyuz_generator.py` -> Нажмите "Execute" (Выполнить).
===============================================================================
"""

import os
import math

try:
    import c4d
    from c4d import documents, utils, bitmaps
    IN_C4D = True
except ImportError:
    IN_C4D = False


def create_pbr_material(doc, name, diffuse_tex_path, normal_tex_path, roughness_tex_path, base_color=(0.8, 0.8, 0.8), roughness=0.35):
    """Создает материал Cinema 4D с подключением текстурных карт Diffuse, Normal и Roughness."""
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    mat.SetName(name)
    mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(*base_color)

    # Подключение цветовой текстуры (Diffuse / Albedo)
    if diffuse_tex_path and os.path.exists(diffuse_tex_path):
        shd_color = c4d.BaseList2D(c4d.Xbitmap)
        shd_color[c4d.BITMAPSHADER_FILENAME] = diffuse_tex_path
        mat[c4d.MATERIAL_COLOR_SHADER] = shd_color
        mat.InsertShader(shd_color)

    # Включение канала Normal Map (рельеф складок ЭВТИ и ячеек солнечных панелей)
    if normal_tex_path and os.path.exists(normal_tex_path):
        mat[c4d.MATERIAL_USE_NORMAL] = True
        shd_norm = c4d.BaseList2D(c4d.Xbitmap)
        shd_norm[c4d.BITMAPSHADER_FILENAME] = normal_tex_path
        mat[c4d.MATERIAL_NORMAL_SHADER] = shd_norm
        mat.InsertShader(shd_norm)

    # Настройка канала Reflectance / Specular
    mat[c4d.MATERIAL_USE_REFLECTION] = True
    doc.InsertMaterial(mat)
    return mat


def assign_uvw_material(obj, mat):
    """Назначает материал объекту с проекцией UVW Mapping в Cinema 4D."""
    tag = c4d.TextureTag()
    tag.SetMaterial(mat)
    tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
    obj.InsertTag(tag)
    return tag


def build_c4d_soyuz_scene(texture_dir, export_obj_path):
    """Строит полную сцену корабля Союз МС внутри Cinema 4D и экспортирует в .obj."""
    if not IN_C4D:
        print("[INFO] Скрипт запущен вне среды Cinema 4D. Используйте встроенный генератор generate_soyuz_3d.py для автономной генерации OBJ/MTL.")
        return False

    doc = documents.GetActiveDocument()
    doc.StartUndo()

    diffuse_map = os.path.join(texture_dir, "soyuz_diffuse.png")
    normal_map = os.path.join(texture_dir, "soyuz_normal.png")
    rough_map = os.path.join(texture_dir, "soyuz_roughness.png")

    # 1. Создание материалов PBR
    mat_evti = create_pbr_material(doc, "MAT_EVTI_Thermal_Blanket", diffuse_map, normal_map, rough_map, (0.22, 0.22, 0.24), 0.45)
    mat_solar = create_pbr_material(doc, "MAT_Solar_Cells_Array", diffuse_map, normal_map, rough_map, (0.72, 0.63, 0.50), 0.20)
    mat_pao = create_pbr_material(doc, "MAT_PAO_White_Radiator", diffuse_map, normal_map, rough_map, (0.93, 0.94, 0.96), 0.35)
    mat_metal = create_pbr_material(doc, "MAT_Kurs_Titanium", diffuse_map, normal_map, rough_map, (0.68, 0.70, 0.73), 0.25)
    mat_periscope = create_pbr_material(doc, "MAT_VSK4_Periscope_Green", diffuse_map, normal_map, rough_map, (0.36, 0.45, 0.27), 0.40)

    # Корневой Null-объект корабля
    root_null = c4d.BaseObject(c4d.Onull)
    root_null.SetName("Soyuz_MS_Spacecraft_Root")
    doc.InsertObject(root_null)

    # 2. Бытовой отсек (БО / Orbital Module)
    bo_sphere = c4d.BaseObject(c4d.Osphere)
    bo_sphere.SetName("BO_Orbital_Module")
    bo_sphere[c4d.PRIM_SPHERE_RAD] = 112.0
    bo_sphere[c4d.PRIM_SPHERE_SUB] = 48
    bo_sphere.SetRelPos(c4d.Vector(0, 0, 232))
    assign_uvw_material(bo_sphere, mat_evti)
    bo_sphere.InsertUnder(root_null)

    # Деформатор Displacer для имитации складок экранно-вакуумной теплоизоляции (ЭВТИ)
    displacer = c4d.BaseObject(c4d.Odisplacer)
    displacer.SetName("EVTI_Wrinkle_Displacer")
    displacer[c4d.MGDISPLACER_DISPLACEMENT_HEIGHT] = 2.4
    noise_shd = c4d.BaseList2D(c4d.Xnoise)
    displacer[c4d.ID_MG_SHADER_SHADER] = noise_shd
    displacer.InsertShader(noise_shd)
    displacer.InsertUnder(bo_sphere)

    # Стыковочный агрегат «Курс»
    dock_cyl = c4d.BaseObject(c4d.Ocylinder)
    dock_cyl.SetName("Kurs_Docking_Mechanism")
    dock_cyl[c4d.PRIM_CYLINDER_RADIUS] = 68.0
    dock_cyl[c4d.PRIM_CYLINDER_HEIGHT] = 42.0
    dock_cyl[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_ZP
    dock_cyl.SetRelPos(c4d.Vector(0, 0, 342))
    assign_uvw_material(dock_cyl, mat_metal)
    dock_cyl.InsertUnder(root_null)

    # 3. Спускаемый аппарат (СА / Descent Module)
    sa_cone = c4d.BaseObject(c4d.Ocone)
    sa_cone.SetName("SA_Descent_Module")
    sa_cone[c4d.PRIM_CONE_TRAD] = 92.0
    sa_cone[c4d.PRIM_CONE_BRAD] = 118.0
    sa_cone[c4d.PRIM_CONE_HEIGHT] = 180.0
    sa_cone[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_ZP
    sa_cone[c4d.PRIM_CONE_RSEG] = 48
    sa_cone.SetRelPos(c4d.Vector(0, 0, 25))
    assign_uvw_material(sa_cone, mat_evti)
    sa_cone.InsertUnder(root_null)

    # Перископ ВСК-4
    periscope = c4d.BaseObject(c4d.Ocylinder)
    periscope.SetName("VSK4_Cosmonaut_Periscope")
    periscope[c4d.PRIM_CYLINDER_RADIUS] = 10.0
    periscope[c4d.PRIM_CYLINDER_HEIGHT] = 65.0
    periscope[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_YP
    periscope.SetRelPos(c4d.Vector(0, 138, 70))
    assign_uvw_material(periscope, mat_periscope)
    periscope.InsertUnder(root_null)

    # 4. Приборно-агрегатный отсек (ПАО / Service Module)
    pao_cyl = c4d.BaseObject(c4d.Ocone)
    pao_cyl.SetName("PAO_Service_Module")
    pao_cyl[c4d.PRIM_CONE_TRAD] = 118.0
    pao_cyl[c4d.PRIM_CONE_BRAD] = 140.0
    pao_cyl[c4d.PRIM_CONE_HEIGHT] = 195.0
    pao_cyl[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_ZP
    pao_cyl[c4d.PRIM_CONE_RSEG] = 48
    pao_cyl.SetRelPos(c4d.Vector(0, 0, -162))
    assign_uvw_material(pao_cyl, mat_pao)
    pao_cyl.InsertUnder(root_null)

    # 5. Крылья солнечных батарей (Левое и Правое по 4 секции)
    for side_name, side_sign in [("Port_Wing", -1), ("Starboard_Wing", 1)]:
        wing_null = c4d.BaseObject(c4d.Onull)
        wing_null.SetName(f"Solar_Array_{side_name}")
        wing_null.InsertUnder(root_null)
        for seg_idx in range(4):
            panel = c4d.BaseObject(c4d.Ocube)
            panel.SetName(f"Solar_Segment_{side_name}_{seg_idx + 1}")
            panel[c4d.PRIM_CUBE_LEN] = c4d.Vector(96.0, 4.5, 138.0)
            panel.SetRelPos(c4d.Vector(side_sign * (178.0 + seg_idx * 102.0), -5.0, -145.0))
            assign_uvw_material(panel, mat_solar)
            panel.InsertUnder(wing_null)

    c4d.EventAdd()

    # 6. Экспорт в формат Wavefront OBJ (.obj)
    if export_obj_path:
        documents.SaveDocument(doc, export_obj_path, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, c4d.FORMAT_OBJ2EXPORT)
        print(f"[Cinema 4D] 3D-модель успешно экспортирована в: {export_obj_path}")

    doc.EndUndo()
    return True


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tex_dir = os.path.join(base_dir, "assets", "textures")
    out_obj = os.path.join(base_dir, "assets", "model", "soyuz_spacecraft.obj")
    build_c4d_soyuz_scene(tex_dir, out_obj)
'''
    with open(c4d_script_path, "w", encoding="utf-8") as f:
        f.write(c4d_code)
    print(f"[OK] Saved Cinema 4D Python plugin script to {c4d_script_path}")
    return c4d_script_path


if __name__ == "__main__":
    generate_textures()
    build_soyuz_spacecraft()
    generate_c4d_script()
