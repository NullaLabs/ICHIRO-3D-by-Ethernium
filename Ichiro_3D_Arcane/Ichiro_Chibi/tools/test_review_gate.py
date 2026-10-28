"""Regression cases: valid geometry, reversed normals, hair-depth jump, bad data."""
import copy
import unittest
from validate_review_packet import inspect_mesh


class GateTests(unittest.TestCase):
    def setUp(self):
        self.mesh = dict(name='fixture', positions=[0,0,0, 1,0,0, 1,1,0, 0,1,0],
                         quadFaces=[[0,1,2,3]])

    def test_outward_quad(self):
        self.assertFalse(inspect_mesh(self.mesh)['blocked'])

    def test_reversed_quad(self):
        self.mesh['quadFaces'][0].reverse()
        self.assertIn('back_facing_frontal_faces', inspect_mesh(self.mesh)['reasons'])

    def test_local_depth_outlier(self):
        # Three quads: ordinary edges dominate median, isolated displaced vertex.
        self.mesh['positions'] += [2,0,0, 2,1,0, 3,0,0, 3,1,30]
        self.mesh['quadFaces'] += [[1,4,5,2], [4,6,7,5]]
        self.assertIn('depth_discontinuity_requires_review', inspect_mesh(self.mesh)['reasons'])

    def test_invalid_index(self):
        self.mesh['quadFaces'][0][0] = 99
        with self.assertRaises(ValueError): inspect_mesh(self.mesh)

    def test_nonfinite_position(self):
        self.mesh['positions'][0] = float('nan')
        with self.assertRaises(ValueError): inspect_mesh(self.mesh)

    def test_no_mutation(self):
        before = copy.deepcopy(self.mesh)
        inspect_mesh(self.mesh)
        self.assertEqual(before, self.mesh)


if __name__ == '__main__':
    unittest.main()
