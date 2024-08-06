""" Tests for a simulation with a drivaer object. """

import pytest
import pyvista as pv

import windtunnel

MESH_PATH = "assets/test_objects/drivaer.obj"


@pytest.fixture(scope="module", name="windtunnel_task")
def windtunnel_task_fixture():
    wind_tunnel = windtunnel.WindTunnel()
    transformations = wind_tunnel.set_object(MESH_PATH,
                                             rotate_z_degrees=0,
                                             normalize=True,
                                             center=True)
    assert transformations is not None

    task = wind_tunnel.simulate(wind_speed_ms=30,
                                num_iterations=50,
                                resolution=3,
                                machine_group_name=None)
    assert task is not None

    yield task, transformations


@pytest.mark.slow
@pytest.mark.dependency()
def test_task_status(windtunnel_task):
    task, _ = windtunnel_task
    task.wait()
    assert task.get_status() == "success"


@pytest.fixture(scope="module", name="windtunnel_outputs")
@pytest.mark.dependency(depends=["test_task_status"])
def windtunnel_outputs_fixture(windtunnel_task):
    task, _ = windtunnel_task
    output_dir = task.download_outputs()
    outputs = windtunnel.WindTunnelOutputs(output_dir)
    yield outputs


@pytest.mark.slow
@pytest.mark.dependency(depends=["test_task_status"])
def test_force_coefficients(windtunnel_outputs):
    force_coefficients = windtunnel_outputs.get_force_coefficients()
    assert force_coefficients is not None

    moment = force_coefficients.get("Moment", None)
    drag = force_coefficients.get("Drag", None)
    lift = force_coefficients.get("Lift", None)
    front_lift = force_coefficients.get("Front Lift", None)
    rear_lift = force_coefficients.get("Rear Lift", None)

    assert moment is not None
    assert drag is not None
    assert lift is not None
    assert front_lift is not None
    assert rear_lift is not None

    assert moment == pytest.approx(0.038, rel=1e-2)
    assert drag == pytest.approx(0.354, rel=1e-2)
    assert lift == pytest.approx(0.300, rel=1e-2)
    assert front_lift == pytest.approx(0.188, rel=1e-2)
    assert rear_lift == pytest.approx(0.111, rel=1e-2)


@pytest.mark.slow
@pytest.mark.dependency(depends=["test_task_status"])
def test_openfoam_mesh(windtunnel_outputs):
    pressure_field_mesh = windtunnel_outputs.get_openfoam_object_mesh()

    assert isinstance(pressure_field_mesh, pv.PolyData)
    assert pressure_field_mesh.n_points > 0 or pressure_field_mesh.n_cells > 0


@pytest.mark.slow
@pytest.mark.dependency(depends=["test_task_status", "test_openfoam_mesh"])
def test_reverse_transformation(windtunnel_task, windtunnel_outputs):
    _, transformations = windtunnel_task
    original_mesh = pv.read(MESH_PATH)
    pressure_field_mesh = windtunnel_outputs.get_interpolated_pressure_field()

    scaling_factor = transformations["scaling_factor"]
    rotate_z_degrees = transformations["rotate_z_degrees"]
    displace_vector = transformations["displace_vector"]
    displace_vector = [-x for x in displace_vector]

    pressure_field_mesh = pressure_field_mesh.scale(1 / scaling_factor)
    pressure_field_mesh = pressure_field_mesh.rotate_z(-rotate_z_degrees)
    pressure_field_mesh = pressure_field_mesh.translate(displace_vector)

    original_bbox = original_mesh.bounds
    pressure_field_bbox = pressure_field_mesh.bounds

    for orig_dim, press_dim in zip(original_bbox, pressure_field_bbox):
        for orig_val, press_val in zip(orig_dim, press_dim):
            pytest.approx(abs(orig_val - press_val), rel=1e-2)


@pytest.mark.slow
@pytest.mark.dependency(depends=["test_task_status"])
def test_interpolated_pressure_field_mesh(windtunnel_outputs):
    pressure_field_mesh = windtunnel_outputs.get_interpolated_pressure_field()

    assert isinstance(pressure_field_mesh, pv.PolyData)
    assert pressure_field_mesh.n_points > 0 or pressure_field_mesh.n_cells > 0


@pytest.mark.slow
@pytest.mark.dependency(depends=["test_task_status"])
def test_streamlines_mesh(windtunnel_outputs):
    streamlines_mesh = windtunnel_outputs.get_streamlines()

    assert isinstance(streamlines_mesh, pv.PolyData)
    assert streamlines_mesh.n_points > 0 or streamlines_mesh.n_cells > 0
