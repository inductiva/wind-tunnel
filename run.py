"""Example run of a WindTunnel scenario based on Inductiva API."""

from absl import app
from absl import logging

import windtunnel


def main(_):
    # Initialize the scenario
    wind_tunnel = windtunnel.WindTunnel()

    # Submit the simulation task
    task = wind_tunnel.simulate(object_path="assets/vehicle.obj",
                                wind_speed_ms=10,
                                num_iterations=50,
                                resolution=3)

    # Wait for the task to finish
    task.wait()

    # Download all of the output files of the simulation
    output_dir = task.download_outputs()

    # Post-process methods: Render the pressure field over the object
    output = windtunnel.WindTunnelOutput(output_dir, 50)

    pressure_field = output.get_object_pressure_field()
    pressure_field.render()


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    app.run(main)
