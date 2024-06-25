"""Pre-processing utilities."""
from collections import namedtuple
from typing import Optional

import pyvista as pv
import trimesh
import vtk

vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)

# dimensions in meters
NORMALIZED_X_MAX = 10.0
NORMALIZED_Y_MAX = 2.0
NORMALIZED_Z_MAX = 1.0


# Object properties to be used in the simulation.
# path: Path to the transformed object file.
# area: Projected area of the object into the inlet face.
# length: Length of the object in the x-axis.
ObjectProperties = namedtuple("ObjectProperties", [
    "path", "area", "length", "original_z_displacement", "scaling_factor",
    "rotate_angle"
])


def _get_scaling_factor(mesh: pv.PolyData) -> float:
    """
    Calculate the scaling factor required to normalize the mesh dimensions.

    Returns the most restrictive scaling factor to ensure the entire mesh fits
    within the specified bounds.

    Args:
        mesh (pv.PolyData): The input mesh to be normalized.

    Returns:
        float: The scaling factor to apply to the mesh.
    """
    x_dimension = mesh.bounds[1] - mesh.bounds[0]
    y_dimension = mesh.bounds[3] - mesh.bounds[2]
    z_dimension = mesh.bounds[5] - mesh.bounds[4]

    # Calculate the scaling factors for each axis
    scaling_factor_x = NORMALIZED_X_MAX / x_dimension
    scaling_factor_y = NORMALIZED_Y_MAX / y_dimension
    scaling_factor_z = NORMALIZED_Z_MAX / z_dimension

    # Use the most restrictive scaling factor
    return min(scaling_factor_x, scaling_factor_y, scaling_factor_z)


def set_object_position(mesh, rotate_angle: float = 0):
    """Set object in the correct position and orientation in the wind tunnel.

    Args:
        mesh: pyvista.PolyData mesh representing the object.
        rotate_angle: Angle to rotate the object around the z-axis.
    """

    # CSM input objects need to be corrected so that they face the inlet.
    mesh = mesh.rotate_x(90)

    original_z_displacement = mesh.bounds[4]

    # Set the input object on the floor of the wind tunnel - z=0.
    mesh = mesh.translate([0, 0, -original_z_displacement])
    mesh = mesh.rotate_z(rotate_angle)

    scaling_factor = _get_scaling_factor(mesh)
    mesh = mesh.scale(scaling_factor)

    return mesh, original_z_displacement, scaling_factor


def compute_projected_area(mesh: pv.PolyData, face_normal):
    """Compute the projected area of an object.

    Args:
        mesh: pyvista.PolyData mesh representing the object.
    """

    # Compute roughly the projected area of the object. Slice the object mesh at
    # its center, which provides an outline curve of the object. Then fill it
    # with a simple mesh and compute the area of the filled mesh.
    mesh_slice = mesh.slice(origin=mesh.center, normal=face_normal)
    filled_slice = mesh_slice.delaunay_2d()
    area = filled_slice.area

    return area


def get_object_properties(object_path: str, mesh: pv.PolyData,
                          original_z_displacement: float, scaling_factor: float,
                          rotate_angle: float):
    """Get the properties of the object to be used in the simulation.

    Args:
        object_path: Path to the object file.
        mesh: pyvista.PolyData mesh representing the object.
    """

    # Compute project area into the inlet face
    area = compute_projected_area(mesh, face_normal=(1, 0, 0))

    # Length of the object in x-direction
    length = mesh.bounds[1] - mesh.bounds[0]

    return ObjectProperties(object_path, area, length, original_z_displacement,
                            scaling_factor, rotate_angle)


def prepare_object(
    source_object_path: str,
    rotate_angle: float = 0,
    dest_object_path: Optional[str] = None,
) -> ObjectProperties:
    """Prepare the object to set the conditions for the simulation.

    There are two steps performed:
    - Rotate the object into the correct orientation, and then, according to
    user input. By default, the rotated object is saved in the same location as
    the source object.
    - Compute the project area of the object into the inlet face.
    """
    dest_object_path = dest_object_path or source_object_path

    mesh = pv.read(source_object_path)
    if mesh is None:
        raise RuntimeError(f"Failed to read object from {source_object_path}")

    mesh, original_z_displacement, scaling_factor = set_object_position(
        mesh, rotate_angle)

    properties = get_object_properties(dest_object_path, mesh,
                                       original_z_displacement, scaling_factor,
                                       rotate_angle)

    # pyvista does not support saving to .obj format
    # mesh.save(dest_object_path)
    # Instead, use trimesh to save the mesh to .obj format
    trimesh_mesh = trimesh.Trimesh(vertices=mesh.points,
                                   faces=mesh.faces.reshape((-1, 4))[:, 1:])
    trimesh.exchange.export.export_mesh(trimesh_mesh, dest_object_path)
    # print(f"Object saved to {dest_object_path}")

    # This requires (on Debian / Ubuntu):
    # $ sudo apt install libgl1-mesa-glx xvfb
    #pv.start_xquartz()
    # pl = pv.Plotter(off_screen=True)
    # pl.add_mesh(mesh)
    # pl.export_obj(dest_object_path)
    # pl.close()

    return properties
