"""
Handles loading force coefficients, generating streamlines, and interpolating
pressure fields over simulation meshes.
"""

import os
import pathlib

import numpy as np
import pyvista as pv


class WindTunnelOutputs:
    """
    Manages WindTunnel simulation outputs.

    Provides methods to load results, including force coefficients, streamlines,
    and pressure fields, from a WindTunnel simulation output directory.

    Attributes:
        simulation_path (str): Path to simulation output directory.
        time_steps (int): Number of time steps in the simulation.
        domain_mesh (pv.PolyData): Domain mesh from the simulation.
        object_mesh (pv.PolyData): Object mesh from the simulation.
    """

    def __init__(self, simulation_path: str):
        """
        Initializes WindTunnelOutputs with the simulation directory.

        Args:
            simulation_path (str): Path to simulation output directory.
        """
        self._simulation_path = simulation_path
        self._time_steps = self._get_num_time_steps()
        self._domain_mesh, self._object_mesh = self._get_output_meshes()

    def get_force_coefficients(self):
        """
        Loads force coefficients from the simulation output.

        Returns:
            dict: Force coefficients including 'Moment', 'Drag', 'Lift',
            'Front Lift', and 'Rear Lift'.
        """
        force_coefficients_path = os.path.join(self._simulation_path,
                                               "postProcessing", "forceCoeffs1",
                                               "0", "forceCoeffs.dat")
        coefficients = np.loadtxt(force_coefficients_path)[-1]
        coefficients_labels = [
            "Moment", "Drag", "Lift", "Front Lift", "Rear Lift"
        ]
        coefficients_dict = dict(
            zip(coefficients_labels, map(float, coefficients[1:])))

        return coefficients_dict

    def get_input_mesh(self):
        """
        Retrieves the input object mesh.

        Returns:
            pv.PolyData: Input object mes.
        """
        input_mesh_path = os.path.join(
            self._simulation_path, "constant", "triSurface", "object.obj"
        )
        input_mesh = pv.read(input_mesh_path)
        return input_mesh

    def get_streamlines(self,
                        n_points=100,
                        initial_step_length=1,
                        source_radius=1.1,
                        source_center=(0, 0, 0),
                        streamline_radius=0.005):
        """
        Generates streamlines from the domain mesh.

        Args:
            n_points (int, optional): Number of streamlines. Defaults to 100.
            initial_step_length (float, optional): Initial step length.
                                                   Defaults to 1.
            source_radius (float, optional): Radius of seeding sphere.
                                             Defaults to 1.1.
            source_center (tuple, optional): Center of seeding sphere.
                                             Defaults to (0, 0, 0).
            streamline_radius (float, optional): Radius of streamlines.
                                                 Defaults to 0.005.

        Returns:
            pv.PolyData: Streamlines as tube-shaped meshes.
        """
        streamlines_mesh = self._domain_mesh.streamlines(
            max_time=self._time_steps,
            n_points=n_points,
            initial_step_length=initial_step_length,
            source_radius=source_radius,
            source_center=source_center)
        streamlines = streamlines_mesh.tube(radius=streamline_radius)
        return streamlines

    def get_openfoam_object_mesh(self):
        """
        Retrieves the pressure field over the domain mesh.

        Returns:
            pv.PolyData: Object mesh with pressure field data.
        """
        return self._object_mesh

    def get_interpolated_pressure_field(self):
        """
        Interpolates pressure field over the object mesh points.

        Returns:
            pv.PolyData: Object mesh with interpolated pressure field.
        """
        input_mesh_path = os.path.join(self._simulation_path, "constant",
                                       "triSurface", "object.obj")
        input_mesh = pv.read(input_mesh_path)

        interpolated_mesh = input_mesh.interpolate(self._object_mesh,
                                                   sharpness=10,
                                                   radius=0.1,
                                                   n_points=1,
                                                   strategy="closest_point")

        return interpolated_mesh

    def _get_num_time_steps(self):
        """
        Retrieves the number of time steps of the simulation.

        Returns:
            int: Number of time steps.
        """
        force_coefficients_path = os.path.join(self._simulation_path,
                                               "postProcessing", "forceCoeffs1",
                                               "0", "forceCoeffs.dat")
        coefficients = np.loadtxt(force_coefficients_path)
        num_time_steps = int(coefficients[-1][0])

        return num_time_steps

    def _get_output_meshes(self):
        """
        Retrieves domain and object mesh info at steady-state.

        Returns:
            tuple: Domain and object mesh as pv.PolyData objects.
        """
        # The OpenFOAM data reader from PyVista requires that a file named
        # "foam.foam" exists in the simulation output directory.
        # Create this file if it does not exist.
        foam_file_path = os.path.join(self._simulation_path, "foam.foam")
        pathlib.Path(foam_file_path).touch(exist_ok=True)

        reader = pv.OpenFOAMReader(foam_file_path)
        reader.set_active_time_value(self._time_steps)

        full_mesh = reader.read()
        domain_mesh = full_mesh["internalMesh"]
        object_mesh = full_mesh["boundary"]["object"]

        return domain_mesh, object_mesh
