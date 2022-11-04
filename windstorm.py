'''
Write a doc string here.
'''
import copy
from dataclasses import dataclass
import pandas as pd

SPEED_COL10 = 'Avg Wind Speed @ 10m [m/s]'
DATE_COL = 'Date (MM/DD/YYYY)'
# DATE_COL = 'DOY'
TIME_COL = 'MST'
DIR_COL10 = 'Avg Wind Direction @ 10m [deg]'


class Windstorm:
    '''Can create windstorm objects using start and stop indices. Properties are speed and direction'''
    def __init__(self,
                 df: pd.DataFrame,
                 start_index: int,
                 stop_index: int,
                 speed_col_name=SPEED_COL10):
        self._df = df
        self.start_index = start_index
        self.stop_index = stop_index
        self.speed_col_name = speed_col_name

    @property
    def data(self):
        return self._df[self.start_index: self.stop_index]

    @property
    def speed(self):
        return self.data[self.speed_col_name]

    @property
    def direction(self):
        return self.data[DIR_COL10]

    def merge(self, storm2):
        self.start_index = min(self.start_index, storm2.start_index)
        self.stop_index = max(self.stop_index, storm2.stop_index)
        return self

    @property
    def duration(self):
        return self.stop_index - self.start_index

    def __repr__(self):
        return ''.join([
                f'Storm start:\t{self._df[DATE_COL][self.start_index]}',
                f' {self._df[TIME_COL][self.start_index]}',
                f'\tend:\t{self._df[DATE_COL][self.stop_index]}',
                f' {self._df[TIME_COL][self.stop_index]}',
                f'\t\tduration: {self.duration} minutes\t' 
                ])

    def __str__(self):
        return self.__repr__() + '\n' + str(self.speed)

    @staticmethod
    def storms_by_threshold(df, threshold: float, speed_col_name=SPEED_COL10):
        above = False
        speeds = df[speed_col_name]
        for index, speed in enumerate(speeds):
            if not above and (speed >= threshold):
                above = True
                start = index
            if above and (speed < threshold):
                above = False
                yield Windstorm(df, start, index,
                                speed_col_name=speed_col_name)
        if above:
            yield Windstorm(df, start, index, speed_col_name=speed_col_name)


@dataclass
class Lull:
    start: int
    stop: int
    df: pd.DataFrame

    @property
    def duration(self):
        return self.stop - self.start

    def __repr__(self):
        return f'Lull(start={self.start}, stop={self.stop})'


class WindstormWithLulls(Windstorm):
    def __init__(self,
                 df,
                 start_index,
                 stop_index,
                 lulls=[],
                 speed_col_name=SPEED_COL10):
        self._df = df
        self.start_index = start_index
        self.stop_index = stop_index
        self.speed_col_name = speed_col_name
        self.lulls = lulls

    def __repr__(self):
        return super().__repr__() + f'with {len(self.lulls)} lulls'

    def merge(self, storm2: Windstorm):
        if (
                min(self.stop_index, storm2.stop_index) <
                max(self.start_index, storm2.start_index)
        ):
            # we have a lull between them
            self.lulls.append(
                Lull(min(self.stop_index, storm2.stop_index),
                     max(self.start_index, storm2.start_index),
                     self._df))
        self.lulls += storm2.lulls
        super().merge(storm2)
        return self

    @staticmethod
    def from_windstorm(storm: Windstorm):
        return WindstormWithLulls(
                storm._df,
                storm.start_index,
                storm.stop_index,
                [],
                speed_col_name=storm.speed_col_name)

    @staticmethod
    def storms_by_threshold(
            df,
            speed_threshold: float,
            lull_threshold: float,
            speed_col_name=SPEED_COL10):
        storms = (WindstormWithLulls.from_windstorm(storm)
                  for storm in
                  Windstorm.storms_by_threshold(
                      df,
                      speed_threshold,
                      speed_col_name))

        current_storm = next(storms)
        returned = False
        for next_storm in storms:
            if next_storm.start_index - current_storm.stop_index < lull_threshold:
                # combine the two
                current_storm.merge(next_storm)
                returned = False
            else:
                yield current_storm
                returned = True
                current_storm = next_storm
        if not returned:
            yield current_storm


    def __add__(self, storm2):
        return copy.copy(self).merge(storm2)

    def __radd__(self, num):
        if num == 0:
            return self
        else:
            raise ValueError(f'Cannot add  {self.__repr__()} and {num.__repr__()}')


if __name__ == '__main__':
    df = pd.read_csv('2022April_data.txt')
    storm = Windstorm(df, 0, 150)
    storm2 = WindstormWithLulls(df, 100, 200, lulls=[(120, 130), (140, 160)])
    storm3 = WindstormWithLulls(df, 250, 280, lulls=[(252, 255)])
    storms = list(Windstorm.storms_by_threshold(df, 10))
    storms_with_lulls = [storm
                         for storm in 
                         WindstormWithLulls.storms_by_threshold(df, 10, 720)
                         if storm.duration >= 60]

    for storm in storms_with_lulls:
        print(storm)
