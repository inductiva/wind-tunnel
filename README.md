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

# Submit a simulation task at low resolution and
# small number of iterations.
task = wind_tunnel.simulate(object_path="assets/f1_car.obj",
                            wind_speed_ms=10,
                            num_iterations=50,
                            resolution=3)

# Wait for the task to finish
task.wait()

# Download all of the output files of the simulation
output_dir = task.download_outputs()

```

In this code snippet, we are using the `WindTunnel` to configure the
simulation files for OpenFOAM, the F1 car and
simulation parameters and simulating via **Inductiva API**. This scenario is a
toy example that can be extended to more complex simulation scenarios, (e.g.,
add rotation of wheels to the vehicle). 


**Disclaimer**: For the sake of time the simulations performed here are low resolution and don't represent any practical real-world application.

To learn more about the `inductiva` package, check the
[Inductiva API documentation](https://github.com/inductiva/inductiva/wiki).
