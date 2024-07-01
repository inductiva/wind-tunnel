"""Example run of a WindTunnel scenario based on Inductiva API."""

import inductiva
from absl import app, flags, logging

import windtunnel
from windtunnel import postprocessing

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

    coeff = postprocessing.get_force_coefficients(output_dir)

    print('Force Coefficients:')
    for key, value in coeff.items():
        print(f'{key}: {value}')

    # pylint: disable=unused-variable
    domain_mesh, object_mesh = postprocessing.get_output_mesh(output_dir)

    visualizer = windtunnel.WindTunnelVisualizer(-6, 14, -5, 5, 0, 8)
    # visualizer.add_mesh(domain_mesh, opacity=0.5, show_edges=True)
    # "p" for pressure field.
    # visualizer.add_mesh(object_mesh, color="red", opacity=0.5, scalars="p")

    pressure_field_mesh = postprocessing.get_interpolated_pressure_field(
        output_dir, object_mesh)
    visualizer.add_mesh(pressure_field_mesh,
                        color='red',
                        opacity=1,
                        scalars='p')

    visualizer.show()


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
