from pyvistaqt import QtInteractor

# class for visualizing the 3D mesh using PyVistaQt in the application interface
class CrochetMeshViewer:
    def __init__(self, parent):
        self.plotter = QtInteractor(parent)
        self.plotter.set_background("white")

    # property for getting the visualization widget
    @property
    def widget(self):
        return self.plotter

    # method for displaying the 3D mesh in the visualizer
    def display(self, mesh):
        if mesh is None:
            return

        self.plotter.clear()

        surface = mesh.clean()
        surface = surface.smooth(
            n_iter=30,
            relaxation_factor=0.08,
            boundary_smoothing=False,
            feature_smoothing=False,
        )
        surface = surface.compute_normals(
            cell_normals=False,
            point_normals=True,
            inplace=False,
        )

        self.plotter.add_mesh(
            surface,
            color="lightblue",
            show_edges=True,
            opacity=0.85,
            smooth_shading=True,
        )
        self.plotter.add_axes()
        self.plotter.show_grid()
        self.set_camera_position(surface)
        self.plotter.render()

    # method for closing the visualizer
    def close(self):
        self.plotter.close()

    # method for setting the optimal camera position
    def set_camera_position(self, surface):
        bounds = surface.bounds

        x_size = max(bounds[1] - bounds[0], 1.0)
        y_size = max(bounds[3] - bounds[2], 1.0)
        z_size = max(bounds[5] - bounds[4], 1.0)

        cx, cy, cz = surface.center

        self.plotter.camera_position = [
            (cx + x_size * 1.2, cy - y_size * 1.6, cz + z_size * 0.35),
            (cx, cy, cz),
            (0, 0, 1),
        ]
