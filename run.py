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

    print(
        f"To visualize results, run:\n python view_outputs.py --task_id {task.id}"
    )


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    app.run(main)
