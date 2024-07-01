"""Example batch run of a WindTunnel scenario based on Inductiva API."""

from absl import app, flags, logging

import windtunnel

FLAGS = flags.FLAGS
flags.DEFINE_boolean('debug', False, 'Enable debug mode')
flags.DEFINE_string('object_path', 'assets/f1_car.obj',
                    'Path to the object file')
flags.DEFINE_string(
    'machine_group_name', None,
    'Machine group to run the simulation on. Defaults to default queue')

# Define a list of configurations
configurations = [
    {
        'wind_speed_ms': 10,
        'rotate_z_degrees': 0,
        'num_iterations': 50,
        'resolution': 3
    },
    {
        'wind_speed_ms': 15,
        'rotate_z_degrees': 10,
        'num_iterations': 75,
        'resolution': 4
    },
    {
        'wind_speed_ms': 8,
        'rotate_z_degrees': 5,
        'num_iterations': 40,
        'resolution': 2
    },
]


def run_simulation(config):
    wind_tunnel = windtunnel.WindTunnel()
    task = wind_tunnel.simulate(object_path=FLAGS.object_path,
                                wind_speed_ms=config['wind_speed_ms'],
                                rotate_z_degrees=config['rotate_z_degrees'],
                                num_iterations=config['num_iterations'],
                                resolution=config['resolution'],
                                machine_group_name=FLAGS.machine_group_name)
    return task.id  # Return the task ID for logging or further processing


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    task_ids = []
    for i, config in enumerate(configurations):
        task_id = run_simulation(config)
        task_ids.append(task_id)
        print(f'Submitted simulation {i+1}. Task ID: {task_id}')

    print('To visualize the results, run:\n'
          'python view_outputs.py --task_id <task_id>\n')


if __name__ == '__main__':
    logging.set_verbosity(logging.WARNING)
    app.run(main)
