"""Unit tests of the pre_processing submodule."""
import math

import pytest
import pyvista as pv

from windtunnel import pre_processing

RESOLUTION = 1000


@pytest.mark.parametrize(
    "radius",
    [0.5, 1, 5, 30],
)
def test_compute_projected_area_sphere(radius):
    sphere = pv.Sphere(
        radius=radius,
        theta_resolution=RESOLUTION,
        phi_resolution=RESOLUTION,
    )

    expected_area = math.pi * radius**2
    computed_area = pre_processing.compute_projected_area(sphere,
                                                          projection_plane="X")
    assert computed_area == pytest.approx(expected_area, rel=1e-2)


@pytest.mark.parametrize(
    "radius,height",
    [(10, 20), (10, 100), (30, 10), (9999, 10)],
)
def test_compute_projected_area_cylinder_top(radius, height):
    cylinder = pv.Cylinder(
        radius=radius,
        height=height,
        resolution=RESOLUTION,
    )
    expected_area = math.pi * radius**2
    computed_area = pre_processing.compute_projected_area(cylinder,
                                                          projection_plane="X")

    assert computed_area == pytest.approx(expected_area, rel=1e-2)


@pytest.mark.parametrize(
    "radius,height",
    [(10, 20), (10, 100), (30, 10), (9999, 10)],
)
def test_compute_projected_area_cylinder_side(radius, height):
    cylinder = pv.Cylinder(
        radius=radius,
        height=height,
        resolution=RESOLUTION,
    )

    expected_area = 2 * radius * height
    computed_area = pre_processing.compute_projected_area(cylinder,
                                                          projection_plane="Y")

    assert computed_area == pytest.approx(expected_area, rel=1e-2)


@pytest.mark.parametrize(
    "object_path",
    [
        "assets/test_objects/cube.obj", "assets/test_objects/sphere.obj",
        "assets/test_objects/ellipsoid.obj", "assets/test_objects/bike.obj",
        "assets/test_objects/drivaer.obj"
    ],
)
def test_compute_projected_area_test_objects(object_path):
    object_name = object_path.split("/")[-1]
    assert object_name in [
        "cube.obj",
        "sphere.obj",
        "ellipsoid.obj",
        "bike.obj",
        "drivaer.obj",
    ]

    expected_projected_area = {
        "cube.obj": 1.0,
        "sphere.obj": 0.79,
        "ellipsoid.obj": 0.79,
        "bike.obj": 0.644,
        "drivaer.obj": 2.16
    }

    mesh = pv.read(object_path)
    mesh, _ = pre_processing.move_mesh_to_origin(mesh)
    computed_area = pre_processing.compute_projected_area(mesh,
                                                          projection_plane="X")
    expected_area = expected_projected_area[object_name]

    assert computed_area == pytest.approx(expected_area, rel=1e-2)
