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
from dataclasses import asdict, dataclass
import shutil
from typing import Optional

import inductiva
from inductiva import resources, simulators

from .pre_processing import prepare_object
import tempfile

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


@dataclass
class RectangularBox:
    """Rectangular box dimensions in 3D space."""

    x_min: float = -6
    x_max: float = 14
    y_min: float = -5
    y_max: float = 5
    z_min: float = 0
    z_max: float = 8

    def __post_init__(self):
        assert self.x_min < self.x_max
        assert self.y_min < self.y_max
        assert self.z_min < self.z_max

    def to_dict(self):
        """Converts the object to a dictionary."""
        return asdict(self)


class WindTunnel:
    """WindTunnel scenario."""

    def __init__(self, inputs_dir: str = "./inductiva_input/"):
        """Initializes the `WindTunnel` scenario object.
        """
        self._walls = RectangularBox()
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
        num_iterations: int,
        resolution: int,
        on: Optional[resources.MachineGroup] = None,
    ):
        """Simulates the wind tunnel scenario synchronously.

        Args:
            object_path: Path to object inserted in the wind tunnel.
            wind_speed_ms: Velocity of the air flow in m/s.
            num_iterations: Number of iterations to run the simulation.
            resolution: Resolution of the simulation grid.
            on: Machine group to run the simulation on.
        """

        # Some temporarily hardcoded values
        rotate_angle = 0
        num_vcpus = 4

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        obj_dir = os.path.join(temp_dir, "constant/triSurface/")
        os.makedirs(obj_dir)
        processed_object_path = os.path.join(obj_dir, "object.obj")

        object_properties = prepare_object(object_path, rotate_angle,
                                           processed_object_path)

        inductiva.TemplateManager.render_dir(
            TEMPLATE_DIR,
            temp_dir,
            wind_speed=wind_speed_ms,
            num_iterations=num_iterations,
            resolution=resolution,
            num_subdomains=
            num_vcpus,  # Number of subdomains for parallel processing
            object_properties=object_properties,
            **self._walls.to_dict(),
        )

        task = simulators.OpenFOAM().run(input_dir=temp_dir,
                                         on=on,
                                         commands=self.get_commands(),
                                         n_vcpus=num_vcpus,
                                         use_hwthreads=False)

        task_dir = os.path.join(self._inputs_dir, task.id)
        os.makedirs(task_dir, exist_ok=True)
        shutil.move(temp_dir, task_dir)

        return task
