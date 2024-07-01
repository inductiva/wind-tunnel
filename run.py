"""Example run of a WindTunnel scenario based on Inductiva API."""

from absl import app, flags, logging

import windtunnel

FLAGS = flags.FLAGS
flags.DEFINE_boolean('debug', False, 'Enable debug mode')
flags.DEFINE_boolean('display', False,
                     'Open PyVista window with inputs visualization')
flags.DEFINE_string('object_path', 'assets/f1_car.obj',
                    'Path to the object file')
flags.DEFINE_integer('wind_speed_ms', 10, 'Wind speed in meters per second')
flags.DEFINE_integer('resolution', 3, 'Resolution of the simulation')
flags.DEFINE_integer('rotate_z_degrees', 0,
                     'Rotation angle around the Z-axis in degrees')
flags.DEFINE_integer('num_iterations', 50,
                     'Number of iterations to run the simulation')
flags.DEFINE_string(
    'machine_group_name', None,
    'Machine group to run the simulation on. Defaults to default queue')


def _check_flags():
    if FLAGS.wind_speed_ms <= 0:
        raise ValueError('Wind speed must be greater than 0')
    if FLAGS.wind_speed_ms > 100:
        raise ValueError('Wind speed must be less than 100')
    if FLAGS.resolution < 3:
        raise ValueError('Resolution must be 3 or greater')
    if FLAGS.resolution > 5:
        raise ValueError('Resolution must be 5 or less')
    if FLAGS.num_iterations < 50:
        raise ValueError('Number of iterations must be 50 or greater')


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    _check_flags()

    # Initialize the scenario
    wind_tunnel = windtunnel.WindTunnel()

    # Submit the simulation task
    task = wind_tunnel.simulate(object_path=FLAGS.object_path,
                                wind_speed_ms=FLAGS.wind_speed_ms,
                                rotate_z_degrees=FLAGS.rotate_z_degrees,
                                num_iterations=FLAGS.num_iterations,
                                resolution=FLAGS.resolution,
                                display=FLAGS.display,
                                machine_group_name=FLAGS.machine_group_name)

    print(f'To visualize results, run:\n\n'
          f'python view_outputs.py --task_id {task.id}\n')


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
