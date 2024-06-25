# Wind Tunnel via Inductiva API

Wind tunnels are central for the development and testing of vehicle aerodynamics -
from your everyday commuter car to the high-performance F1 car.
With **Inductiva API** users can simplify their simulation workflow and build their
custom virtual wind tunnels to accelerate the discovery of new designs.

<div align="center">
<img src="assets/f1.gif" width=500 height=300 alt="F1 simulation">
</div>

In this repository, we assume users are familiar with one of the most popular
open-source simulators for virtual wind tunnels, [OpenFOAM](https://www.openfoam.org).
If not, we advise to get acquainted with it through the classical
[motorbike tutorial](https://github.com/OpenFOAM/OpenFOAM-8/tree/master/tutorials/incompressible/simpleFoam/motorBike).

## Virtual wind tunnel simulations

When performing wind tunnel tests - virtual or physical - only a few
parameters are tweaked, for example, changing the airflow velocity for the same
vehicle.
**Inductiva API** provides a powerful mechanism to configure this simulation
from this set of parameters, this workflow is designated as
a **simulation scenario**.

Let's set an F1 car in a toy **wind tunnel** and run a simulation scenario:

```python
import windtunnel


# Create wind tunnel object
wind_tunnel = windtunnel.WindTunnel()

# Submit the simulation task
task = wind_tunnel.simulate(object_path="assets/f1_car.obj",
                            wind_speed_ms=10,
                            num_iterations=50,
                            resolution=3)

# Wait for the task to finish
task.wait()

# Download all of the output files of the simulation
output_dir = task.download_outputs()

```

In this code snippet, we are using the `WindTunnelScenario` to configure the
simulation files for OpenFOAM with the `wind_tunnel` model, the F1 car and
simulation parameters and simulating via **Inductiva API**. This scenario is a
toy example that can be extended to more complex simulation scenarios, (e.g.,
add rotation of wheels to the vehicle). 

In this repository, users will learn how to create a simulation scenario from a
low-level OpenFOAM call via **Inductiva API** to a higher-level structure within
a Python class.

Before starting, make sure to have the `inductiva` package installed and
follow the instructions in the [installation section](docs/0_INSTALL.md).

The **wind tunnel** tour is split into the following steps:
1. [Running OpenFOAM simulations via Inductiva API](docs/1_OPENFOAM_SIM.md)
2. [Templating your simulation files to introduce simple configuration](docs/2_TEMPLATING.md)
3. [Creating a custom wind tunnel scenario with Python](docs/3_WINDTUNNEL_SCENARIO.md)

**Disclaimer**: For the sake of time the simulations performed here are simple and
don't represent any practical real-world application.

To learn more about the `inductiva` package, check the
[Inductiva API documentation](https://github.com/inductiva/inductiva/wiki).
