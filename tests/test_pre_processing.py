"""Unit tests of the pre_processing submodule."""
import math
import os

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
    "filename",
    ["cube.obj", "sphere.obj", "ellipsoid.obj", "bike.obj", "drivaer.obj"],
)
def test_compute_projected_area(filename):
    expected_projected_area = {
        "cube.obj": 1.0,
        "sphere.obj": 0.79,
        "ellipsoid.obj": 0.79,
        "bike.obj": 0.644,
        "drivaer.obj": 2.16
    }
    mesh_path = os.path.join("assets/test_objects", filename)
    mesh = pv.read(mesh_path)
    mesh, _ = pre_processing.move_mesh_to_origin(mesh)
    computed_area = pre_processing.compute_projected_area(mesh,
                                                          projection_plane="X")
    expected_area = expected_projected_area[filename]

    assert computed_area == pytest.approx(expected_area, rel=1e-2)


@pytest.mark.parametrize(
    "filename",
    ["cube.obj", "sphere.obj", "ellipsoid.obj", "bike.obj", "drivaer.obj"],
)
def test_compute_object_length(filename):
    expected_object_length = {
        "cube.obj": 1.0,
        "sphere.obj": 1.0,
        "ellipsoid.obj": 2.0,
        "bike.obj": 2.05,
        "drivaer.obj": 4.61
    }

    mesh_path = os.path.join("assets/test_objects", filename)
    mesh = pv.read(mesh_path)
    mesh, _ = pre_processing.move_mesh_to_origin(mesh)
    computed_length = pre_processing.compute_object_length(mesh)
    expected_length = expected_object_length[filename]
    assert computed_length == pytest.approx(expected_length, rel=1e-2)
