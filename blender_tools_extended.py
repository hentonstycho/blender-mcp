"""Extended Blender tools for material, modifier, and rendering operations."""

import bpy


def get_object_info(object_name: str) -> dict:
    """Get detailed info about a specific object."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"error": f"Object '{object_name}' not found"}

    return {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": obj.visible_get(),
        "materials": [m.name for m in obj.data.materials] if hasattr(obj.data, "materials") else [],
        "modifiers": [mod.name for mod in obj.modifiers],
    }


def set_material(object_name: str, material_name: str, color: list = None) -> dict:
    """Assign or create a material on an object.

    Args:
        object_name: Name of the target object.
        material_name: Name of the material to assign or create.
        color: Optional RGBA list [r, g, b, a] with values 0-1.
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"error": f"Object '{object_name}' not found"}

    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True

    if color and len(color) >= 3:
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            rgba = color if len(color) == 4 else color + [1.0]
            bsdf.inputs["Base Color"].default_value = rgba

    if not hasattr(obj.data, "materials"):
        return {"error": f"Object '{object_name}' does not support materials"}

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return {"status": "ok", "material": mat.name, "object": obj.name}


def add_modifier(object_name: str, modifier_type: str, params: dict = None) -> dict:
    """Add a modifier to an object.

    Args:
        object_name: Name of the target object.
        modifier_type: Blender modifier type, e.g. 'SUBSURF', 'SOLIDIFY', 'BEVEL'.
        params: Optional dict of modifier property name -> value pairs.
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"error": f"Object '{object_name}' not found"}

    try:
        mod = obj.modifiers.new(name=modifier_type.capitalize(), type=modifier_type)
    except Exception as e:
        return {"error": str(e)}

    if params:
        for key, value in params.items():
            if hasattr(mod, key):
                setattr(mod, key, value)

    return {"status": "ok", "modifier": mod.name, "object": obj.name}


def render_scene(output_path: str, resolution_x: int = 1920, resolution_y: int = 1080) -> dict:
    """Render the current scene to a file.

    Args:
        output_path: Absolute file path for the render output (e.g. /tmp/render.png).
        resolution_x: Render width in pixels.
        resolution_y: Render height in pixels.
    """
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = "PNG"

    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        return {"error": str(e)}

    return {"status": "ok", "output_path": output_path}


def set_background_color(color: list) -> dict:
    """Set the world background color.

    Args:
        color: RGB list with values 0-1, e.g. [0.1, 0.1, 0.1].
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node and len(color) >= 3:
        rgba = color + [1.0] if len(color) == 3 else color
        bg_node.inputs["Color"].default_value = rgba

    return {"status": "ok", "color": color}
