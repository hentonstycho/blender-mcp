"""Blender MCP tool definitions and handlers for scene manipulation."""

import json
from typing import Any


def get_scene_info(params: dict) -> dict:
    """Return basic info about the current Blender scene."""
    try:
        import bpy
        scene = bpy.context.scene
        objects = [
            {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "visible": obj.visible_get(),
            }
            for obj in scene.objects
        ]
        return {
            "name": scene.name,
            "frame_current": scene.frame_current,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "object_count": len(objects),
            "objects": objects,
        }
    except Exception as e:
        return {"error": str(e)}


def create_object(params: dict) -> dict:
    """Create a primitive mesh object in the scene."""
    try:
        import bpy
        obj_type = params.get("type", "CUBE").upper()
        name = params.get("name", None)
        # Default to world origin; override with 'location' param as [x, y, z]
        location = params.get("location", [0, 0, 0])
        # Default scale to 1.0 uniform; can be overridden via 'scale' param.
        # I changed the default from None to 1.0 so newly created objects always
        # have an explicit scale applied, making it easier to spot in the outliner.
        scale = params.get("scale", 1.0)

        bpy.ops.object.select_all(action="DESELECT")

        type_map = {
            "CUBE": bpy.ops.mesh.primitive_cube_add,
            "SPHERE": bpy.ops.mesh.primitive_uv_sphere_add,
            "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
            "PLANE": bpy.ops.mesh.primitive_plane_add,
            "CONE": bpy.ops.mesh.primitive_cone_add,
            "TORUS": bpy.ops.mesh.primitive_torus_add,
            # EMPTY is handy as a parent/pivot object
            "EMPTY": bpy.ops.object.empty_add,
            # MONKEY (Suzanne) - useful for quick testing/demos
            "MONKEY": bpy.ops.mesh.primitive_monkey_add,
        }

        if obj_type not in type_map:
            return {"error": f"Unknown object type: {obj_type}"}

        type_map[obj_type](location=tuple(location))
        obj = bpy.context.active_object

        if name:
            obj.name = name

        # Apply optional uniform or per-axis scale after creation
        if scale is not None:
            if isinstance(scale, (int, float)):
                obj.scale = (scale, scale, scale)
            elif len(scale) == 3:
                obj.scale = tuple(scale)

        return {"name": obj.name, "type": obj.type, "location": list(obj.location), "scale": list(obj.scale)}
    except Exception as e:
        return {"error": str(e)}


def delete_object(params: dict) -> dict:
    """Delete an object from the scene by name."""
    try:
        import bpy
        name = params.get("name")
        if not name:
            return {"error": "'name' parameter is required"}

        obj = bpy.data.objects.get(name)
        if obj is None:
            return {"error": f"Ob
