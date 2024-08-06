"""Example batch run of a WindTunnel scenario based on Inductiva API."""

import os

from absl import app, flags, logging

import windtunnel

FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "Enable debug mode")
flags.DEFINE_string("object_path_folder", "assets/test_objects",
                    "Path to the folder with the object file")
flags.DEFINE_integer("wind_speed_ms", 16, "Wind speed in meters per second")
flags.DEFINE_integer("resolution", 3, "Resolution of the simulation")
flags.DEFINE_integer("rotate_z_degrees", 0,
                     "Rotation angle around the Z-axis in degrees")
flags.DEFINE_integer("num_iterations", 50,
                     "Number of iterations to run the simulation")
flags.DEFINE_boolean("display", False, "Display the simulation")
flags.DEFINE_string(
    "machine_group_name", None,
    "Machine group to run the simulation on. Defaults to default queue")


def run_simulation(object_path):
    wind_tunnel = windtunnel.WindTunnel()
    wind_tunnel.set_object(object_path, rotate_z_degrees=FLAGS.rotate_z_degrees)

    if FLAGS.display:
        wind_tunnel.display()

    task = wind_tunnel.simulate(wind_speed_ms=FLAGS.wind_speed_ms,
                                num_iterations=FLAGS.num_iterations,
                                resolution=FLAGS.resolution,
                                machine_group_name=FLAGS.machine_group_name)
    return task


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    folder = FLAGS.object_path_folder
    objects_path = []
    tasks = []

    for filename in os.listdir(folder):
        if filename.endswith(".obj"):
            objects_path.append(os.path.join(folder, filename))

    for object_path in objects_path:
        task = run_simulation(object_path)
        tasks.append(task)

    for object_path, task in zip(objects_path, tasks):
        task.wait()
        output_dir = task.download_outputs()
        outputs = windtunnel.WindTunnelOutputs(output_dir)
        coeffs = outputs.get_force_coefficients()

        print("--------------------")
        print(f"Force coefficients for {object_path}:")
        for key, value in coeffs.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    logging.set_verbosity(logging.WARNING)
    app.run(main)
