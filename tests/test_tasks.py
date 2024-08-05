import time

import pytest

import windtunnel


@pytest.fixture(scope="module")
def wind_tunnel_task():
    wind_tunnel = windtunnel.WindTunnel()
    wind_tunnel.set_object("assets/test_objects/drivaer.obj",
                           rotate_z_degrees=0)

    task = wind_tunnel.simulate(wind_speed_ms=30,
                                num_iterations=50,
                                resolution=3,
                                machine_group_name=None)
    yield task


@pytest.mark.dependency()
def test_task_status(wind_tunnel_task):
    while True:
        if not wind_tunnel_task.is_running():
            assert wind_tunnel_task.get_status() == "success"
            break
        time.sleep(5)


@pytest.fixture(scope="module")
@pytest.mark.dependency(depends=["test_task_status"])
def windtunnel_outputs(wind_tunnel_task):
    output_dir = wind_tunnel_task.download_outputs()
    outputs = windtunnel.WindTunnelOutputs(output_dir)
    yield outputs


@pytest.mark.dependency(depends=["test_task_status", "windtunnel_outputs"])
def test_force_coefficients(windtunnel_outputs):
    force_coefficients = windtunnel_outputs.get_force_coefficients()
    moment = force_coefficients["Moment"]
    drag = force_coefficients["Drag"]
    lift = force_coefficients["Lift"]
    front_lift = force_coefficients["Front Lift"]
    rear_lift = force_coefficients["Rear Lift"]

    assert moment == pytest.approx(0.038, rel=1e-2)
    assert drag == pytest.approx(0.354, rel=1e-2)
    assert lift == pytest.approx(0.300, rel=1e-2)
    assert front_lift == pytest.approx(0.188, rel=1e-2)
    assert rear_lift == pytest.approx(0.111, rel=1e-2)
