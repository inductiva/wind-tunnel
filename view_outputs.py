"""Example run of a WindTunnel scenario based on Inductiva API."""

import inductiva
from absl import app, flags, logging

import windtunnel

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

    outputs = windtunnel.WindTunnelOutputs(output_dir)

    coeff = outputs.get_force_coefficients()
    input_mesh = outputs.get_input_mesh()  # pylint: disable=unused-variable
    openfoam_mesh = outputs.get_openfoam_object_mesh()  # pylint: disable=unused-variable
    pressure_field_mesh = outputs.get_interpolated_pressure_field()
    streamlines_mesh = outputs.get_streamlines()

    print('Force Coefficients:')
    for key, value in coeff.items():
        print(f'{key}: {value}')

    # "p" for pressure field.
    visualizer = windtunnel.WindTunnelVisualizer(-6, 14, -5, 5, 0, 8)
    visualizer.add_mesh(pressure_field_mesh,
                        color='red',
                        opacity=1,
                        scalars='p')
    visualizer.add_mesh(streamlines_mesh, color='blue', opacity=0.5)
    visualizer.show()


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
