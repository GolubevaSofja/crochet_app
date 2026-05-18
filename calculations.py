import math
from dataclasses import dataclass

import numpy as np
import pyvista as pv


# the main class for calculating the 3D surface based on the input data from the gui
@dataclass
class CrochetSurfaceCalculator:
    stitches_per_row: list[int]
    stitch_width: float = 0.67
    row_height: float = 0.67
    visual_roundness: float = 0.75
    end_roundness_strength: float = 0.85
    narrowing_sensitivity: float = 0.85
    min_inner_roundness: float = 0.20
    segments: int | None = None
    profile_count: int | None = None

    # The main method for building the model. It is called in the graphical interface and performs the following steps:
    # - validates the user input data
    # - prepares the parameters for calculation
    # - calculates the row radii
    # - calculates the row heights with visual scaling taken into account
    # - builds the axes for the profile
    # - creates a smoothed radius profile
    # - creates an array of points and faces for the 3D model
    # - returns the finished 3D model as pv.PolyData
    def build(self):
        if len(self.stitches_per_row) < 2:
            return None

        self.prepare_parameters()

        real_radii = self.real_radii()
        max_radius = float(np.max(real_radii))

        if max_radius <= 0:
            return None

        row_count = len(real_radii)
        raw_height = self.row_height * (row_count - 1)

        if raw_height <= 0:
            return None

        height_scale = self.clamp(
            max_radius * 2.0 / raw_height,
            0.55,
            0.90,
        )
        row_t, profile_t, z_profile = self.profile_axes(
            row_count,
            height_scale,
        )
        r_profile = self.radius_profile(
            real_radii,
            row_t,
            profile_t,
        )
        points, faces = self.mesh_data(r_profile, z_profile)

        return pv.PolyData(
            np.array(points),
            np.array(faces),
        )

    # method for preparing parameters
    def prepare_parameters(self):
        self.visual_roundness = self.clamp(self.visual_roundness, 0.0, 1.0)
        self.end_roundness_strength = self.clamp(
            self.end_roundness_strength,
            0.0,
            1.0,
        )
        self.narrowing_sensitivity = self.clamp(
            self.narrowing_sensitivity,
            0.0,
            1.5,
        )
        self.min_inner_roundness = self.clamp(
            self.min_inner_roundness,
            0.0,
            1.0,
        )

        dynamic_segments, dynamic_profile_count = self.calculate_mesh_resolution(
            self.stitches_per_row
        )
        self.segments = self.segments or dynamic_segments
        self.profile_count = self.profile_count or dynamic_profile_count

    # method for calculating the real radii of the rows based on the number of stitches and stitch width
    def real_radii(self):
        return np.array(
            [
                stitches * self.stitch_width / (2 * math.pi)
                for stitches in self.stitches_per_row
            ],
            dtype=float,
        )

    # method for calculating the vertical coordinates of the profile
    def profile_axes(self, row_count, height_scale):
        row_z = self.build_row_z_positions(
            row_count=row_count,
            row_height=self.row_height,
            end_flatness=self.end_roundness_strength,
            height_scale=height_scale,
        )
        row_t = np.linspace(0.0, 1.0, row_count)
        profile_t = np.linspace(0.0, 1.0, self.profile_count)
        z_profile = profile_t * row_z[-1]

        return row_t, profile_t, z_profile

    # method for calculating the radius profile, creates a smooth transition between the real row radius
    def radius_profile(self, real_radii, row_t, profile_t):
        interpolated_radii = self.smooth_array(
            np.interp(profile_t, row_t, real_radii),
            passes=6,
        )
        rounded_radii = self.local_rounded_radii(
            profile_t,
            row_t,
            real_radii,
        )
        row_roundness = self.local_roundness(
            real_radii=real_radii,
            base_roundness=self.visual_roundness,
            narrowing_sensitivity=self.narrowing_sensitivity,
            min_roundness=self.min_inner_roundness,
        )
        profile_roundness = self.smooth_array(
            np.interp(profile_t, row_t, row_roundness),
            passes=6,
        )

        r_profile = (
            interpolated_radii * (1.0 - profile_roundness)
            + rounded_radii * profile_roundness
        )
        r_profile[0] = real_radii[0]
        r_profile[-1] = real_radii[-1]

        r_profile = self.smooth_array(
            r_profile,
            passes=int(8 + self.visual_roundness * 10),
        )
        r_profile[0] = real_radii[0]
        r_profile[-1] = real_radii[-1]

        return r_profile

    # method for creating an array of points and faces for the 3D model based on the radius profile and vertical coordinates
    def mesh_data(self, r_profile, z_profile):
        theta = np.linspace(
            0.0,
            2.0 * np.pi,
            self.segments,
            endpoint=False,
        )
        points = [
            [
                radius * math.cos(angle),
                radius * math.sin(angle),
                z_value,
            ]
            for radius, z_value in zip(r_profile, z_profile)
            for angle in theta
        ]
        bottom_center_index = len(points)
        top_center_index = None

        points.append([0.0, 0.0, z_profile[0]])

        if self.stitches_per_row[-1] <= 6:
            top_center_index = len(points)
            points.append([0.0, 0.0, z_profile[-1]])

        faces = []
        profile_count = len(r_profile)

        for j in range(profile_count - 1):
            current_ring = j * self.segments
            upper_ring = (j + 1) * self.segments

            for i in range(self.segments):
                faces.extend([
                    4,
                    current_ring + i,
                    current_ring + ((i + 1) % self.segments),
                    upper_ring + ((i + 1) % self.segments),
                    upper_ring + i,
                ])

        for i in range(self.segments):
            faces.extend([
                3,
                bottom_center_index,
                (i + 1) % self.segments,
                i,
            ])

        if top_center_index is not None:
            last_ring = (profile_count - 1) * self.segments

            for i in range(self.segments):
                faces.extend([
                    3,
                    top_center_index,
                    last_ring + i,
                    last_ring + ((i + 1) % self.segments),
                ])

        return points, faces

    # method for smoothing an array of values, used for creating more rounded shapes
    @staticmethod
    def smooth_array(values, passes=6):
        arr = np.array(values, dtype=float)

        for _ in range(passes):
            smoothed = arr.copy()

            for i in range(1, len(arr) - 1):
                smoothed[i] = (
                    arr[i - 1] * 0.25
                    + arr[i] * 0.50
                    + arr[i + 1] * 0.25
                )

            arr = smoothed

        return arr

    # method for calculating the degree to which each row should be rounded
    @classmethod
    def local_roundness(
        cls,
        real_radii,
        base_roundness,
        narrowing_sensitivity=0.85,
        min_roundness=0.20,
    ):
        row_count = len(real_radii)

        if row_count < 5 or float(np.max(real_radii)) <= 0:
            return np.full(row_count, base_roundness, dtype=float)

        roundness = np.full(row_count, base_roundness, dtype=float)

        for group in cls.inner_narrowing_groups(real_radii):
            min_radius, min_indices = cls.group_min(real_radii, group)
            surrounding_radius = cls.surrounding_radius(real_radii, group)

            if surrounding_radius <= 0:
                continue

            narrowing_amount = max(
                0.0,
                (surrounding_radius - min_radius) / surrounding_radius,
            )
            reduced_roundness = base_roundness * (
                1.0 - narrowing_amount * narrowing_sensitivity
            )

            for row_index in min_indices:
                roundness[row_index] = reduced_roundness

        roundness = np.maximum(roundness, min_roundness)

        return cls.smooth_array(roundness, passes=2)

    # A method that builds a more rounded radius profile
    # It divides the shape into sections between narrowing points and creates a spherical curve for each section
    @classmethod
    def local_rounded_radii(cls, profile_t, row_t, real_radii):
        section_edges = cls.profile_section_edges(real_radii, row_t)
        rounded_radii = np.interp(profile_t, row_t, real_radii)

        for section_index in range(len(section_edges) - 1):
            start_t = section_edges[section_index]
            end_t = section_edges[section_index + 1]

            if end_t <= start_t:
                continue

            if section_index == len(section_edges) - 2:
                mask = (profile_t >= start_t) & (profile_t <= end_t)
            else:
                mask = (profile_t >= start_t) & (profile_t < end_t)

            if not np.any(mask):
                continue

            start_radius = float(np.interp(start_t, row_t, real_radii))
            end_radius = float(np.interp(end_t, row_t, real_radii))
            row_mask = (row_t >= start_t) & (row_t <= end_t)
            section_max = max(start_radius, end_radius)

            if np.any(row_mask):
                section_max = max(
                    section_max,
                    float(np.max(real_radii[row_mask])),
                )

            local_t = (profile_t[mask] - start_t) / (end_t - start_t)
            end_line = (
                start_radius * (1.0 - local_t)
                + end_radius * local_t
            )
            sphere_core = np.sqrt(
                np.clip(
                    1.0 - (2.0 * local_t - 1.0) ** 2,
                    0.0,
                    1.0,
                )
            )

            rounded_radii[mask] = (
                end_line + (section_max - end_line) * sphere_core
            )

        return rounded_radii

    # A method for determining the locations where the profile should be divided into sections for forming rounded shapes
    @classmethod
    def profile_section_edges(cls, real_radii, row_t):
        section_edges = [0.0]

        for group in cls.inner_narrowing_groups(real_radii):
            _, min_indices = cls.group_min(real_radii, group)
            section_edges.append(float(np.mean(row_t[min_indices])))

        terminal_neck_start = cls.terminal_neck_start(real_radii)

        if terminal_neck_start is not None:
            section_edges.append(float(row_t[terminal_neck_start]))

        section_edges.append(1.0)

        return sorted(set(section_edges))

    # method for determining whether the profile contains long sections with the same radius
    @classmethod
    def terminal_neck_start(
        cls,
        real_radii,
        min_depth=0.25,
        min_run_length=4,
    ):
        max_radius = float(np.max(real_radii))

        if max_radius <= 0:
            return None

        max_indices = np.where(np.isclose(real_radii, max_radius))[0]
        search_start = int(max_indices[-1]) + 1

        for run_start in range(search_start, len(real_radii) - min_run_length):
            run_radius = real_radii[run_start]

            if run_radius > max_radius * (1.0 - min_depth):
                continue

            run_end = run_start

            while (
                run_end + 1 < len(real_radii)
                and np.isclose(real_radii[run_end + 1], run_radius)
            ):
                run_end += 1

            if run_end - run_start + 1 >= min_run_length:
                return run_start

        return None

    # method for detecting internal narrowings of the shape
    @classmethod
    def inner_narrowing_groups(cls, real_radii, min_depth=0.12):
        groups = []
        current_group = []

        for i in range(1, len(real_radii) - 1):
            left_max = float(np.max(real_radii[:i]))
            right_max = float(np.max(real_radii[i + 1:]))
            surrounding_radius = min(left_max, right_max)
            narrowing_depth = 0.0

            if surrounding_radius > 0:
                narrowing_depth = (
                    surrounding_radius - real_radii[i]
                ) / surrounding_radius

            if narrowing_depth >= min_depth:
                current_group.append(i)
            elif current_group:
                groups.append(current_group)
                current_group = []

        if current_group:
            groups.append(current_group)

        return groups

    # method for finding the minimum radius in a group and the indices where it occurs
    @staticmethod
    def group_min(real_radii, group):
        min_radius = float(np.min(real_radii[group]))
        min_indices = [
            row_index
            for row_index in group
            if np.isclose(real_radii[row_index], min_radius)
        ]

        return min_radius, min_indices

    # method for finding the radius surrounding the narrowing group
    @staticmethod
    def surrounding_radius(real_radii, group):
        left_max = float(np.max(real_radii[:group[0]]))
        right_max = float(np.max(real_radii[group[-1] + 1:]))

        return min(left_max, right_max)

    # method for rounding a value to the nearest multiple of a given step
    @staticmethod
    def round_to_multiple(value, step):
        return int(round(value / step) * step)

    # method for automatically determining the optimal mesh resolution
    @classmethod
    def calculate_mesh_resolution(cls, stitches_per_row):
        segments = cls.round_to_multiple(max(stitches_per_row) * 1.3, 8)
        profile_count = len(stitches_per_row) * 6

        return (
            max(24, min(segments, 96)),
            max(40, min(profile_count, 220)),
        )

    # method for calculating the vertical positions of rows based on height
    @staticmethod
    def build_row_z_positions(
        row_count,
        row_height,
        end_flatness=0.85,
        height_scale=0.72,
    ):
        if row_count < 2:
            return np.array([0.0], dtype=float)

        t = np.linspace(0.0, 1.0, row_count)
        curved_t = 0.5 - 0.5 * np.cos(np.pi * t)
        mixed_t = (1.0 - end_flatness) * t + end_flatness * curved_t

        return mixed_t * row_height * (row_count - 1) * height_scale

    # method for limiting a value to specified bounds
    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))
