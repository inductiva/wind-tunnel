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
                            rotate_z_degrees=0,
                            num_iterations=50,
                            resolution=3,
                            display=True)

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


## Installation

1.	Clone the repository:
```
git clone https://github.com/inductiva/wind-tunnel.git
cd wind-tunnel
```

2.  Install the package:
```
pip install .
```


## Scripts Overview
The repository includes several scripts to facilitate running and managing your wind tunnel simulations:

### `run.py`

Quickly run standalone wind tunnel simulations using this script. It accepts the following arguments:

- `--display`: Opens a pyvista window with the windtunnel simulation
- `--object_path`: Path to the input object file
- `--wind_speed_ms`: Wind speed in meters per second (default: 10)
- `--resolution`: Resolution of the OpenFOAM simulation (default: 3, max: 5)
- `--rotate_z_degrees`: Rotation angle around the Z-axis in degrees (default: 0)
- `--num_iterations`: Number of iterations to run the simulation (default: 50)
- `--machine_group_name`: Machine group to run the simulation on (default: default queue)

Example usage:
```bash 
python run.py --object_path assets/f1_car.obj --display
```


### `batch_run`:

Submit multiple simulations with varying arguments. This script is useful for exploring different scenarios efficiently. Inside the script you can change the simulation arguments.

- `--object_path`: Path to the input object file
- `--machine_group_name`: Machine group to run the simulation on (default: default queue)

```bash 
python batch_run.py --object_path assets/f1_car.obj 
```


### `view_outputs.py`

Display the results of a completed simulation in a PyVista window and print the resulting force coefficients. This script waits for the task to finish and requires a `task_id` argument.

```
python view_outputs.py --task_id <task_id>
```

## Running Simulations on Dedicated Hardware
To run simulations on dedicated hardware, you need to start a machine group.

First, list all available machine types with:

```bash 
inductiva resources available
```


### Starting a Machine Group
Note: Spot machines are preemptible but are approximately 5x cheaper. If a machine becomes unavailable during use, the simulation will automatically restart.

Instantiating a `MachineGroup` object with 5 preemptible machines of type c2-standard-32:

```python 
import inductiva

machine_group = inductiva.resources.MachineGroup(
    machine_type="c2-standard-30", num_machines=5, spot=True)
machine_group.start()

print(machine_group.name)

# Don't forget to terminate the machine group after using it:
machine_group.terminate()
```

### Using the Machine Group
After starting the machine group, pass its name to the `run.py` or `batch_run.py` scripts.

```
python run.py --object_path assets/f1_car.obj --machine_group_name <machine_group_name>
```

### Elastic Machine Groups
You can also create an `ElasticMachineGroup`, which scales machines up or down automatically based on the simulation queue.

For more details on running simulations on dedicated hardware, refer to the [Inductiva Machine Group documentation](https://docs.inductiva.ai/en/latest/how_to/run-parallel_simulations.html)

---

**Disclaimer**: For the sake of time the simulations performed here are low resolution and don't represent any practical real-world application.

To learn more about the `inductiva` package, check the
[Inductiva API documentation](https://github.com/inductiva/inductiva/wiki).
