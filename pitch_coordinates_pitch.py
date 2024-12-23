import numpy as np


class PitchCoordinatesPitch:

    def __init__(self, width: float, length: float):
        self.width = width
        self.length = length

    @property
    def pitch_data(self) -> np.ndarray:
        half_width = self.width / 2
        half_length = self.length / 2
        return np.array(
            [
                [-half_width, half_length],
                [half_width, half_length],
                [half_width, -half_length],
                [-half_width, -half_length],
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
