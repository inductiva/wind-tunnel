"""Physical scenario of a configurable wind tunnel simulation.

A wind tunnel is a tool used in aerodynamic research to study the
effects of air moving past solid objects. Here, the tunnel consists
of a box object in 3D space (x, y, z) space, where air flows in the
positive x-direction with a certain velocity.

An arbitrary object is placed within the tunnel, sucht that air flows
around it, as illustrated in the schematic below:
|--------------------------------|
|->          _____               |
|->        _/     |              |
|->_______|_o___O_|______________|

This scenario solves steady-state continuity and momentum equations
(time-independent) with incompressible flow.
The simulation solves the time-independent equations for several
time steps, based on the state of the previous one. The end goal is
to determine the steady-state of the system, i.e., where the flow
does not change in time anymore.

Currently, the following variables are fixed:
- The fluid being inject is air.
- Air only flows in the positive x-direction.
- The flow is incompressible (this seems to be a reasonable approximation
  until about Mach 0.3 which is 102.9 m/s, or 370.44 km/h). 
  See https://www.quora.com/Is-air-an-incompressible-fluid
- Some post-processing of the data occurs at run-time: streamlines,
pressure_field, cutting planes and force coefficients.
"""

import os
import shutil
from typing import Optional

import inductiva
from inductiva import resources, simulators
import pyvista as pv

from . import pre_processing
from .display import WindTunnelVisualizer
import tempfile

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


class WindTunnel:
    """WindTunnel scenario."""

    def __init__(self, inputs_dir: str = "./inductiva_input/"):
        """Initializes the `WindTunnel` scenario object.
        """
        self._walls = {
            "x_min": -6,
            "x_max": 14,
            "y_min": -5,
            "y_max": 5,
            "z_min": 0,
            "z_max": 8
        }
        self._inputs_dir = inputs_dir

    def get_commands(self):

        commands = [
            "runApplication surfaceFeatures",
            "runApplication blockMesh",
            "runApplication decomposePar -copyZero",
            "runParallel snappyHexMesh -overwrite",
            "runParallel potentialFoam",
            "runParallel simpleFoam",
            "runApplication reconstructParMesh -constant",
            "runApplication reconstructPar -latestTime",
        ]
        return commands

    def simulate(
        self,
        object_path: str,
        wind_speed_ms: float,
        rotate_z_degrees: float,
        num_iterations: int,
        resolution: int,
        on: Optional[resources.MachineGroup] = None,
        display: bool = False,
    ):
        """Simulates the wind tunnel scenario synchronously.

        Args:
            object_path: Path to object inserted in the wind tunnel.
            wind_speed_ms: Velocity of the air flow in m/s.
            num_iterations: Number of iterations to run the simulation.
            resolution: Resolution of the simulation grid.
            on: Machine group to run the simulation on.
            display: Whether to display the meshes of object and wind tunnel on
                the screen, before running the simulation.
        """

        # Some temporarily hardcoded values
        num_vcpus = 4  # default queue specific

        mesh = pv.read(object_path)

        if display:
            visualizer = WindTunnelVisualizer(**self._walls)
            visualizer.add_mesh(mesh, color="blue", opacity=0.5)

        # Bounding box of the object is
        mesh, displace_vector, = pre_processing.move_mesh_to_origin(mesh)
        mesh = mesh.rotate_z(rotate_z_degrees)
        mesh, scaling_factor = pre_processing.normalize_mesh(mesh)

        if display:
            visualizer.add_mesh(mesh, color="green")
            visualizer.show()

        # Compute project area into the inlet face
        area = pre_processing.compute_projected_area(mesh,
                                                     face_normal=(1, 0, 0))
        length = pre_processing.compute_object_length(mesh)

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        obj_dir = os.path.join(temp_dir, "constant/triSurface/")
        os.makedirs(obj_dir)
        processed_object_path = os.path.join(obj_dir, "object.obj")
        pre_processing.save_mesh_obj(mesh, processed_object_path)

        inductiva.TemplateManager.render_dir(
            TEMPLATE_DIR,
            temp_dir,
            wind_speed=wind_speed_ms,
            num_iterations=num_iterations,
            resolution=resolution,
            num_subdomains=num_vcpus,  # num subdomains for parallel processing
            area=area,
            length=length,
            **self._walls,
        )

        task = simulators.OpenFOAM().run(input_dir=temp_dir,
                                         on=on,
                                         commands=self.get_commands(),
                                         n_vcpus=num_vcpus,
                                         use_hwthreads=False)

        task_dir = os.path.join(self._inputs_dir, task.id)
        shutil.copytree(temp_dir, task_dir)

        return task
