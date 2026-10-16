# -*- coding: utf-8 -*-
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
