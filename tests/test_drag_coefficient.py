""" Test the drag coefficient calculation for different objects. """

import os

import inductiva
import pytest

import windtunnel


@pytest.fixture(scope="module", name="setup_machine_group")
def setup_machine_group_fixture():
    mg = inductiva.resources.MachineGroup(machine_type="c2d-highcpu-32",
                                          num_machines=1,
                                          spot=False)
    mg.start()

    yield mg.name

    mg.terminate()


@pytest.mark.slow
@pytest.mark.very_slow
@pytest.mark.parametrize(
    "filename, expected_drag_coeff",
    [("cube.obj", 1.05), ("sphere.obj", 0.45), ("ellipsoid.obj", 0.2),
     ("bike.obj", 0.42), ("drivaer.obj", 0.28)],
)
def test_windtunnel_task(setup_machine_group, filename, expected_drag_coeff):
    object_path = os.path.join("assets/test_objects", filename)
    wind_tunnel = windtunnel.WindTunnel()
    wind_tunnel.set_object(object_path,
                           rotate_z_degrees=0,
                           normalize=False,
                           center=True)

    task = wind_tunnel.simulate(wind_speed_ms=16,
                                num_iterations=300,
                                resolution=5,
                                machine_group_name=setup_machine_group)

    task.wait()
    output_dir = task.download_outputs()
    outputs = windtunnel.WindTunnelOutputs(output_dir)
    force_coefficients = outputs.get_force_coefficients()

    drag = force_coefficients.get("Drag", None)
    assert drag == pytest.approx(expected_drag_coeff, rel=2e-1)
