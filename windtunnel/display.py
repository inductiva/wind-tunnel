import pyvista as pv

import vtk

vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)


def get_x_aligned_rectangle(x, y_min, y_max, z_min, z_max):
    y_mean = (y_min + y_max) / 2
    z_mean = (z_min + z_max) / 2
    y_length = y_max - y_min
    z_length = z_max - z_min
    plane = pv.Plane(center=(x, y_mean, z_mean),
                     direction=(1, 0, 0),
                     i_size=z_length,
                     j_size=y_length)
    return plane


def get_y_aligned_rectangle(y, x_min, x_max, z_min, z_max):
    x_mean = (x_min + x_max) / 2
    z_mean = (z_min + z_max) / 2
    x_length = x_max - x_min
    z_length = z_max - z_min
    plane = pv.Plane(center=(x_mean, y, z_mean),
                     direction=(0, 1, 0),
                     i_size=z_length,
                     j_size=x_length)
    return plane


def get_z_aligned_rectangle(z, x_min, x_max, y_min, y_max):
    x_mean = (x_min + x_max) / 2
    y_mean = (y_min + y_max) / 2
    x_length = x_max - x_min
    y_length = y_max - y_min
    plane = pv.Plane(center=(x_mean, y_mean, z),
                     direction=(0, 0, 1),
                     i_size=x_length,
                     j_size=y_length)
    return plane


class WindTunnelVisualizer:

    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float,
                 z_min: float, z_max: float):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

        self.plt = pv.Plotter()
        self.plt.add_axes()
        self._add_walls()
        self._add_origin_sphere()

    def _add_origin_sphere(self, radius: float = 0.1, color: str = "black"):
        sphere = pv.Sphere(radius=radius, center=(0, 0, 0))
        self.plt.add_mesh(sphere, color=color)

    def add_mesh(self,
                 mesh: pv.PolyData,
                 color: str = "blue",
                 opacity: float = 1.0,
                 show_edges: bool = False):
        self.plt.add_mesh(mesh,
                          color=color,
                          opacity=opacity,
                          show_edges=show_edges)

    def _add_walls(self, opacity: float = 0.5):
        plane = get_x_aligned_rectangle(self.x_min, self.y_min, self.y_max,
                                        self.z_min, self.z_max)
        self.plt.add_mesh(plane, color="red", opacity=opacity)
        plane = get_x_aligned_rectangle(self.x_max, self.y_min, self.y_max,
                                        self.z_min, self.z_max)
        self.plt.add_mesh(plane, color="red", opacity=opacity, show_edges=True)

        plane = get_y_aligned_rectangle(self.y_min, self.x_min, self.x_max,
                                        self.z_min, self.z_max)
        self.plt.add_mesh(plane,
                          color="green",
                          opacity=opacity,
                          show_edges=True)

        plane = get_z_aligned_rectangle(self.z_min, self.x_min, self.x_max,
                                        self.y_min, self.y_max)
        self.plt.add_mesh(plane,
                          color="blue",
                          opacity=opacity,
                          show_edges=True)

    def set_camera_position(self, camera_position):
        self.plt.camera_position = camera_position

    def show(self):
        self.plt.show()
