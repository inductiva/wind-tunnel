"""Example run of a WindTunnel scenario based on Inductiva API."""

from absl import app
from absl import logging

import inductiva
import windtunnel
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_boolean('debug', False, 'Enable debug mode')

flags.DEFINE_string('task_id', None, 'Task ID to wait for', required=True)


def main(_):

    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    task = inductiva.tasks.Task(FLAGS.task_id)
    # Wait for the task to finish
    task.wait()

    # Download all of the output files of the simulation
    output_dir = task.download_outputs()

    # Post-process methods: Render the pressure field over the object
    output = windtunnel.WindTunnelOutput(output_dir, 50)

    domain_mesh, object_mesh = output.get_output_mesh()

    visualizer = windtunnel.WindTunnelVisualizer(-6, 14, -5, 5, 0, 8)
    # visualizer.add_mesh(domain_mesh,
    #                     color="blue",
    #                     opacity=0.5,
    #                     show_edges=True)
    visualizer.add_mesh(object_mesh, color="red", opacity=1.0)
    visualizer.show()

    pressure_field = output.get_object_pressure_field()
    pressure_field.render()


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    app.run(main)
