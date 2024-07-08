"""Post-processing tools of fluid dynamics steady-state simulations.

This class implements various post-processing capabilities for
the visualizations associated. Namely:
    - Pressure over object;
    - Cutting plane;
    - Stream lines.

Current Support - OpenFOAM
"""
import os
import pathlib

import numpy as np
import pyvista as pv

# Map physical field names to OpenFOAM notation
PHYSICAL_FIELD = {"pressure": "p", "velocity": "U"}


def get_output_mesh(sim_output_path: str):
    """Get domain and object mesh from sim_output_path."""

    # The OpenFOAM data reader from PyVista requires that a file named
    # "foam.foam" exists in the simulation output directory.
    # Create this file if it does not exist.
    foam_file_path = os.path.join(sim_output_path, "foam.foam")
    pathlib.Path(foam_file_path).touch(exist_ok=True)

    reader = pv.OpenFOAMReader(foam_file_path)
    time_value = get_num_time_steps(sim_output_path)
    reader.set_active_time_value(time_value)

    full_mesh = reader.read()
    domain_mesh = full_mesh["internalMesh"]
    object_mesh = full_mesh["boundary"]["object"]

    return domain_mesh, object_mesh


def get_interpolated_pressure_field(sim_output_path: str,
                                    object_mesh: pv.PolyData):
    """Get a pressure scalar field over mesh points of the object.

    Returns:
        pv.PolyData: The object mesh with the pressure field interpolated
        from the values in the input mesh.
    """

    input_mesh_path = os.path.join(sim_output_path, "constant", "triSurface",
                                   "object.obj")
    input_mesh = pv.read(input_mesh_path)

    interpolated_mesh = input_mesh.interpolate(object_mesh,
                                               sharpness=10,
                                               radius=0.1,
                                               n_points=1,
                                               strategy="closest_point")

    return interpolated_mesh


def get_num_time_steps(sim_output_path: str):
    """Get the number of time steps of the simulation."""

    force_coefficients_path = os.path.join(sim_output_path, "postProcessing",
                                           "forceCoeffs1", "0",
                                           "forceCoeffs.dat")
    coefficients = np.loadtxt(force_coefficients_path)
    num_time_steps = int(coefficients[-1][0])

    return num_time_steps


def get_force_coefficients(sim_output_path: str):
    """Load the force coefficients.

    Returns:
        An array with the following collumns Cm, Cd, Cl, Cl(f), Cl(r).
    """

    force_coefficients_path = os.path.join(sim_output_path, "postProcessing",
                                           "forceCoeffs1", "0",
                                           "forceCoeffs.dat")
    coefficients = np.loadtxt(force_coefficients_path)[-1]
    coefficients_labels = ["Moment", "Drag", "Lift", "Front Lift", "Rear Lift"]
    coefficients_dict = dict(
        zip(coefficients_labels, map(float, coefficients[1:])))

    return coefficients_dict


def get_streamlines(
        sim_output_path: str,
        domain_mesh: pv.PolyData,
        n_points: int = 100,
        initial_step_length: float = 1,
        source_radius: float = 1.1,
        source_center: tuple = (0, 0, 0),
        streamline_radius: float = 0.005,
):
    """
    Generate streamlines based on simulation output and domain mesh.

    Parameters:
    sim_output_path (str): Path to the simulation output file.
    domain_mesh (pv.PolyData): PolyData object representing the domain mesh.
    n_points (int, optional): Number of points to generate each streamline.
    initial_step_length (float, optional): Initial step length.
    source_radius (float, optional): Radius of the source region.
    source_center (tuple, optional): Center coordinates of the source region.
    streamline_radius (float, optional): Radius of the generated streamlines.

    Returns:
    pv.PolyData: PolyData object representing the generated streamlines.
    """
    num_time_steps = get_num_time_steps(sim_output_path)
    streamlines_mesh = domain_mesh.streamlines(
        max_time=num_time_steps,
        n_points=n_points,
        initial_step_length=initial_step_length,
        source_radius=source_radius,
        source_center=source_center,
    )
    streamlines = streamlines_mesh.tube(radius=streamline_radius)
    return streamlines


def get_flow_slices(domain_mesh: pv.PolyData,
                    object_mesh: pv.PolyData,
                    plane: str = "xz"):
    object_height = object_mesh.bounds[5] - object_mesh.bounds[4]

    if plane == "xy":
        normal = (0, 0, 1)
        origin = (0, 0, object_height / 2)
    elif plane == "yz":
        normal = (1, 0, 0)
        origin = (0, 0, 0)
    elif plane == "xz":
        normal = (0, 1, 0)
        origin = (0, 0, 0)
    else:
        raise ValueError("Invalid plane. Choose from 'xy', 'yz', 'xz'.")

    flow_slice = domain_mesh.slice(normal=normal, origin=origin)
    return flow_slice
