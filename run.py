"""Example run of a WindTunnel scenario based on Inductiva API."""

from absl import app
from absl import logging

import windtunnel
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_boolean('debug', False, 'Enable debug mode')


def main(_):

    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    # Initialize the scenario
    wind_tunnel = windtunnel.WindTunnel()

    # Submit the simulation task
    task = wind_tunnel.simulate(object_path="assets/f1_car.obj",
                                wind_speed_ms=10,
                                rotate_z_degrees=0,
                                num_iterations=50,
                                resolution=3,
                                debug=FLAGS.debug)
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
