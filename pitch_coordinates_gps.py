import utm
import numpy as np
from scipy.spatial.transform import Rotation

from pitch_coordinates_pitch import PitchCoordinatesPitch


class PitchCoordinatesGPS:

    def __init__(self, pitch_coordinate_set: dict[str, dict[str, float]]):
        self.pitch_data = self._pitch_coordinate_data(pitch_coordinate_set)
        self._pitch_data_utm = self._gps_to_utm_data(self.pitch_data)

    @staticmethod
    def _pitch_coordinate_data(
        pitch_coordinate_set: dict[str, dict[str, float]]
    ) -> np.ndarray:
        return np.array(
            [
                [
                    pitch_coordinate_set["topLeft"]["latitude"],
                    pitch_coordinate_set["topLeft"]["longitude"],
                ],
                [
                    pitch_coordinate_set["topRight"]["latitude"],
                    pitch_coordinate_set["topRight"]["longitude"],
                ],
                [
                    pitch_coordinate_set["bottomRight"]["latitude"],
                    pitch_coordinate_set["bottomRight"]["longitude"],
                ],
                [
                    pitch_coordinate_set["bottomLeft"]["latitude"],
                    pitch_coordinate_set["bottomLeft"]["longitude"],
                ],
            ]
        )

    def top_left(self) -> np.ndarray:
        return self.pitch_data[0]

    def top_right(self) -> np.ndarray:
        return self.pitch_data[1]

    def bottom_right(self) -> np.ndarray:
        return self.pitch_data[2]

    def bottom_left(self) -> np.ndarray:
        return self.pitch_data[3]

    def _utm_zone_number(self) -> int:
        top_left = self.top_left()
        return utm.latlon_to_zone_number(top_left[0], top_left[1])

    def _utm_zone_letter(self) -> str:
        top_left = self.top_left()
        return utm.latitude_to_zone_letter(top_left[0])

    def _gps_to_utm_data(self, location_data: np.ndarray) -> np.ndarray:
        utm_eastings = []
        utm_northings = []
    
        for lat, lon in location_data:
            easting, northing, _, _ = utm.from_latlon(lat, lon)
            utm_eastings.append(easting)
            utm_northings.append(northing)
    
        return np.column_stack([utm_eastings, utm_northings])

    @property
    def width(self) -> float:
        return np.linalg.norm(self._pitch_data_utm[0] - self._pitch_data_utm[1])

    @property
    def length(self) -> float:
        return np.linalg.norm(self._pitch_data_utm[0] - self._pitch_data_utm[3])

    def pitch_coordinates_pitch(self) -> PitchCoordinatesPitch:
        return PitchCoordinatesPitch(self.width, self.length)

    def _utm_to_pitch_transformation_matrix(self) -> np.ndarray:
        # Ripped straight from https://stackoverflow.com/questions/20546182/how-to-perform-coordinates-affine-transformation-using-python-part-2
        primary = self._pitch_data_utm
        secondary = self.pitch_coordinates_pitch().pitch_data

        pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
        X = pad(primary)
        Y = pad(secondary)
        A, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)

        return A

    def _ned_to_pitch_rotation(self) -> Rotation:
        ned_horizontal = self._pitch_data_utm[1] - self._pitch_data_utm[0]
        angle = np.arctan2(ned_horizontal[1], ned_horizontal[0])
        return Rotation.from_euler("z", -angle, degrees=False)

    def gps_to_pitch_data(self, location_data: np.ndarray) -> np.ndarray:
        utm_data = self._gps_to_utm_data(location_data)
        transformation_matrix = self._utm_to_pitch_transformation_matrix()

        padding = np.ones((utm_data.shape[0], 1))
        padded_utm_data = np.hstack([utm_data, padding])

        padded_pitch_data = padded_utm_data @ transformation_matrix
        pitch_data = padded_pitch_data[:, :-1]

        return pitch_data
