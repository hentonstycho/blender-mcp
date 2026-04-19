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
        location = params.get("location", [0, 0, 0])

        bpy.ops.object.select_all(action="DESELECT")

        type_map = {
            "CUBE": bpy.ops.mesh.primitive_cube_add,
            "SPHERE": bpy.ops.mesh.primitive_uv_sphere_add,
            "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
            "PLANE": bpy.ops.mesh.primitive_plane_add,
            "CONE": bpy.ops.mesh.primitive_cone_add,
            "TORUS": bpy.ops.mesh.primitive_torus_add,
        }

        if obj_type not in type_map:
            return {"error": f"Unknown object type: {obj_type}"}

        type_map[obj_type](location=tuple(location))
        obj = bpy.context.active_object

        if name:
            obj.name = name

        return {"name": obj.name, "type": obj.type, "location": list(obj.location)}
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
            return {"error": f"Object '{name}' not found"}

        bpy.data.objects.remove(obj, do_unlink=True)
        return {"deleted": name}
    except Exception as e:
        return {"error": str(e)}


def set_object_transform(params: dict) -> dict:
    """Set location, rotation, or scale of an object."""
    try:
        import bpy
        name = params.get("name")
        if not name:
            return {"error": "'name' parameter is required"}

        obj = bpy.data.objects.get(name)
        if obj is None:
            return {"error": f"Object '{name}' not found"}

        if "location" in params:
            obj.location = tuple(params["location"])
        if "rotation" in params:
            obj.rotation_euler = tuple(params["rotation"])
        if "scale" in params:
            obj.scale = tuple(params["scale"])

        return {
            "name": obj.name,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }
    except Exception as e:
        return {"error": str(e)}


# Registry mapping tool names to handler functions
TOOL_REGISTRY: dict[str, Any] = {
    "get_scene_info": get_scene_info,
    "create_object": create_object,
    "delete_object": delete_object,
    "set_object_transform": set_object_transform,
}


def dispatch(tool_name: str, params: dict) -> dict:
    """Dispatch a tool call by name."""
    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: '{tool_name}'"}
    return handler(params)
