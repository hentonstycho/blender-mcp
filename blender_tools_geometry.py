"""Extended Blender geometry tools for MCP server.

Provides functions for mesh manipulation, UV operations,
and geometry-level editing via Blender's Python API.
"""

import bpy
import bmesh
from mathutils import Vector


def subdivide_mesh(object_name: str, cuts: int = 1, smoothness: float = 0.0) -> dict:
    """Subdivide the mesh of a given object.

    Args:
        object_name: Name of the target object.
        cuts: Number of cuts to make (1-10).
        smoothness: Smoothness factor (0.0 = sharp, 1.0 = smooth).

    Returns:
        dict with status and updated face/vertex counts.
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Object '{object_name}' not found"}
    if obj.type != 'MESH':
        return {"error": f"Object '{object_name}' is not a mesh"}

    cuts = max(1, min(cuts, 10))
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=cuts, smoothness=smoothness)
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data
    return {
        "status": "success",
        "object": object_name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
    }


def merge_vertices(object_name: str, threshold: float = 0.001) -> dict:
    """Merge vertices that are within a given distance threshold.

    Args:
        object_name: Name of the target object.
        threshold: Maximum distance between vertices to merge.

    Returns:
        dict with status and vertex count before/after merge.
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Object '{object_name}' not found"}
    if obj.type != 'MESH':
        return {"error": f"Object '{object_name}' is not a mesh"}

    before = len(obj.data.vertices)

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.object.mode_set(mode='OBJECT')

    after = len(obj.data.vertices)
    return {
        "status": "success",
        "object": object_name,
        "vertices_before": before,
        "vertices_after": after,
        "merged": before - after,
    }


def set_origin(object_name: str, origin_type: str = "ORIGIN_CENTER_OF_MASS") -> dict:
    """Set the origin point of an object.

    Args:
        object_name: Name of the target object.
        origin_type: One of 'ORIGIN_GEOMETRY', 'ORIGIN_CENTER_OF_MASS',
                     'ORIGIN_CENTER_OF_VOLUME', 'ORIGIN_CURSOR'.

    Returns:
        dict with status and new origin location.
    """
    valid_types = {
        "ORIGIN_GEOMETRY",
        "ORIGIN_CENTER_OF_MASS",
        "ORIGIN_CENTER_OF_VOLUME",
        "ORIGIN_CURSOR",
    }
    if origin_type not in valid_types:
        return {"error": f"Invalid origin_type '{origin_type}'. Choose from {valid_types}"}

    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Object '{object_name}' not found"}

    # Deselect all, then select target
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type=origin_type)

    loc = obj.location
    return {
        "status": "success",
        "object": object_name,
        "origin_type": origin_type,
        "new_location": {"x": round(loc.x, 4), "y": round(loc.y, 4), "z": round(loc.z, 4)},
    }


def get_mesh_info(object_name: str) -> dict:
    """Return detailed mesh statistics for an object.

    Args:
        object_name: Name of the target object.

    Returns:
        dict with vertex, edge, face counts and bounding box dimensions.
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Object '{object_name}' not found"}
    if obj.type != 'MESH':
        return {"error": f"Object '{object_name}' is not a mesh"}

    mesh = obj.data
    # Bounding box corners in world space
    bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [v.x for v in bbox_world]
    ys = [v.y for v in bbox_world]
    zs = [v.z for v in bbox_world]

    return {
        "object": object_name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "materials": len(mesh.materials),
        "bounding_box": {
            "min": {"x": round(min(xs), 4), "y": round(min(ys), 4), "z": round(min(zs), 4)},
            "max": {"x": round(max(xs), 4), "y": round(max(ys), 4), "z": round(max(zs), 4)},
            "dimensions": {
                "x": round(max(xs) - min(xs), 4),
                "y": round(max(ys) - min(ys), 4),
                "z": round(max(zs) - min(zs), 4),
            },
        },
    }
