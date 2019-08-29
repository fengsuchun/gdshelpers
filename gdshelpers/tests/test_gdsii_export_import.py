import filecmp
import unittest
import numpy as np
from shapely.affinity import translate, rotate

from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.pattern_import import GDSIIImport

from gdshelpers.export.gdsii_export import _real_to_8byte


class GdsTestCase(unittest.TestCase):
    def test_export_import(self):
        waveguide = Waveguide([0, 0], 0, 1)
        for i_bend in range(9):
            waveguide.add_bend(angle=np.pi, radius=60 + i_bend * 40)
        offset = (10, 10)
        angle = np.pi

        cell = Cell('test')
        cell.add_to_layer(1, waveguide)

        sub_cell = Cell('sub_cell')
        sub_cell.add_to_layer(2, waveguide)
        cell.add_cell(sub_cell, origin=(0, 0), angle=0)

        sub_cell2 = Cell('sub_cell2')
        sub_cell2.add_to_layer(3, waveguide)
        cell.add_cell(sub_cell2, origin=offset, angle=angle)

        cell.save(library='gdshelpers', grid_steps_per_micron=10000)

        self.assertTrue(
            waveguide.get_shapely_object().almost_equals(GDSIIImport('test.gds', 'test', 1).get_shapely_object(),
                                                         decimal=3))
        self.assertTrue(
            waveguide.get_shapely_object().almost_equals(GDSIIImport('test.gds', 'test', 2).get_shapely_object(),
                                                         decimal=3))

        self.assertTrue(
            translate(rotate(waveguide.get_shapely_object(), angle, use_radians=True, origin=(0, 0)),
                      *offset).almost_equals(
                GDSIIImport('test.gds', 'test', 3).get_shapely_object(), decimal=3))

    def test_parallel_export(self):
        waveguide = Waveguide([0, 0], 0, 1)
        for i_bend in range(9):
            waveguide.add_bend(angle=np.pi, radius=60 + i_bend * 40)

        cells = [Cell('main')]
        for i in range(10):
            cell = Cell('sub_cell_' + str(i))
            cell.add_to_layer(waveguide)
            cells[-1].add_cell(cell, (10, 10))

        cells[0].save('serial.gds', library='gdshelpers', parallel=False)
        cells[0].save('parallel.gds', library='gdshelpers', parallel=True)

        self.assertTrue(filecmp.cmp('serial.gds', 'parallel.gds'))
