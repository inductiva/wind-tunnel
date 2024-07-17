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
import tempfile
from typing import Optional

import inductiva
import pyvista as pv
from inductiva import simulators

from . import pre_processing, utils
from .display import WindTunnelVisualizer

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Factors used to determine the position of the walls within the wind tunnel

# The object is placed closer to the inlet to avoid wall effects
X_MIN_FACTOR = -0.3
X_MAX_FACTOR = 0.7
# The object is centered in the y-direction
Y_MIN_FACTOR = -0.5
Y_MAX_FACTOR = 0.5
# The object is placed at z=0 and z is always positive
Z_MIN_FACTOR = 0.0
Z_MAX_FACTOR = 1.0

# Factors used to determine the maximum size of the object when normalizing it
# These factors were chosen so that the object fits within a circle of radius 1
# for the default wind tunnel size
MAX_OBJECT_LENGTH_FACTOR = 0.5
MAX_OBJECT_WIDTH_FACTOR = 0.2
MAX_OBJECT_HEIGHT_FACTOR = 0.125


class WindTunnel:
    """WindTunnel scenario."""

    def __init__(self, dimensions: tuple[int, int, int] = (20, 10, 8)):
        """
        Initializes the wind tunnel with given dimensions.
        length, width, height = dimensions

        Parameters:
        - dimensions: A tuple (length, width, height) for the tunnel size.
        """
        self.length, self.width, self.height = dimensions
        self._walls = {
            "x_min": self.length * X_MIN_FACTOR,
            "x_max": self.length * X_MAX_FACTOR,
            "y_min": self.width * Y_MIN_FACTOR,
            "y_max": self.width * Y_MAX_FACTOR,
            "z_min": self.height * Z_MIN_FACTOR,
            "z_max": self.height * Z_MAX_FACTOR,
        }
        self.dimensions = dimensions
        self.object = None
        self.object_area = 0
        self.object_length = 0

    def set_object(self,
                   object_path: str,
                   rotate_z_degrees: float = 0,
                   normalize: bool = True,
                   center: bool = True):
        """Load an object into the windtunnel scenario. Optionally rotates, 
        normalizes, and centers it.

        Args:
            object_path (str): Mesh file path.
            rotate_z_degrees (float): Rotation around Z-axis in degrees.
            normalize (bool): Scales object to unit size if True.
            center (bool): Centers object in simulation space if True.
        """

        mesh = pv.read(object_path)
        displace_vector = [0, 0, 0]
        scaling_factor = 1

        if center:
            mesh, displace_vector, = pre_processing.move_mesh_to_origin(mesh)
        if rotate_z_degrees:
            mesh = mesh.rotate_z(rotate_z_degrees)
        if normalize:
            max_object_dimensions = (self.length * MAX_OBJECT_LENGTH_FACTOR,
                                     self.width * MAX_OBJECT_WIDTH_FACTOR,
                                     self.height * MAX_OBJECT_HEIGHT_FACTOR)
            mesh, scaling_factor = pre_processing.normalize_mesh(
                mesh, max_object_dimensions)

        # Compute project area into the inlet face
        self.object_area = pre_processing.compute_projected_area(
            mesh, face_normal=(1, 0, 0))
        self.object_length = pre_processing.compute_object_length(mesh)

        self.object = mesh
        return {
            "displace_vector": displace_vector,
            "scaling_factor": scaling_factor
        }

    def get_commands(self):
        """
        Returns a list of commands to be executed by openfoam.

        Returns:
            list: A list of commands.
        """
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

    def display(self):
        """Display the wind tunnel scenario."""
        visualizer = WindTunnelVisualizer(**self._walls)
        if self.object:
            visualizer.add_mesh(self.object, color="blue", opacity=0.5)
        visualizer.show()

    def simulate(self,
                 wind_speed_ms: float,
                 num_iterations: int,
                 resolution: int,
                 machine_group_name: Optional[str] = None,
                 inputs_base_dir: Optional[str] = "./inductiva_input"):
        """Runs wind tunnel simulation with specified parameters.

        Parameters:
            wind_speed_ms (float): Air flow speed in m/s.
            num_iterations (int): Simulation iteration count.
            resolution (int): Grid resolution.
            machine_group_name (Optional[str]): Machine group for simulation.
            inputs_base_dir (Optional[str]): Input files directory.
        """
        if not self.object:
            raise ValueError("Object not set. Please set object first.")

        mg = utils.get_machine_group(machine_group_name)
        num_vcpus = utils.get_number_subdomains(mg)

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        obj_dir = os.path.join(temp_dir, "constant/triSurface/")
        os.makedirs(obj_dir)
        object_path = os.path.join(obj_dir, "object.obj")
        pre_processing.save_mesh_obj(self.object, object_path)

        inductiva.TemplateManager.render_dir(
            TEMPLATE_DIR,
            temp_dir,
            wind_speed=wind_speed_ms,
            num_iterations=num_iterations,
            resolution=resolution,
            num_subdomains=num_vcpus,  # num subdomains for parallel processing
            area=self.object_area,
            length=self.object_length,
            **self._walls,
        )

        task = simulators.OpenFOAM().run(input_dir=temp_dir,
                                         on=mg,
                                         commands=self.get_commands(),
                                         n_vcpus=num_vcpus,
                                         use_hwthreads=False)

        task_dir = os.path.join(inputs_base_dir, task.id)
        shutil.copytree(temp_dir, task_dir)

        return task
