"""Unit tests of the pre_processing submodule."""
import math

import pytest
import pyvista as pv

from windtunnel import pre_processing

RESOLUTION = 1000


@pytest.mark.parametrize(
    "radius",
    [1, 5, 30],
)
def test_compute_projected_area_sphere(radius):
    sphere = pv.Sphere(
        radius=radius,
        theta_resolution=RESOLUTION,
        phi_resolution=RESOLUTION,
    )

    expected_area = math.pi * radius**2
    computed_area = pre_processing.compute_projected_area(
        sphere,
        face_normal=(1, 0, 0),
    )
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
    computed_area = pre_processing.compute_projected_area(
        cylinder,
        face_normal=(1, 0, 0),
    )

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
    computed_area = pre_processing.compute_projected_area(
        cylinder,
        face_normal=(0, 1, 0),
    )

    assert computed_area == pytest.approx(expected_area, rel=1e-2)
