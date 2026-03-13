import math
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine.hyperscale_study import HydraCoolHyperscaleStudy


class HydraulicPhysicsValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.study = HydraCoolHyperscaleStudy()

    def test_unesco_density_matches_reference_points(self) -> None:
        reference_points = {
            0.0: 1028.1063314148107,
            20.0: 1024.7630049942754,
            40.0: 1017.9731500486849,
        }
        for temp_c, expected_density in reference_points.items():
            with self.subTest(temp_c=temp_c):
                actual_density = self.study.seawater_density_kgm3(temp_c)
                self.assertAlmostEqual(actual_density, expected_density, places=6)

    def test_unesco_density_decreases_with_temperature(self) -> None:
        cold_density = self.study.seawater_density_kgm3(4.0)
        warm_density = self.study.seawater_density_kgm3(24.0)
        self.assertGreater(cold_density, warm_density)

    def test_swamee_jain_reference_case(self) -> None:
        friction_factor = self.study.darcy_friction_factor(
            reynolds=1.0e6,
            roughness_m=4.5e-5,
            diameter_m=1.0,
        )
        self.assertAlmostEqual(friction_factor, 0.012592025334891893, places=9)

    def test_laminar_friction_factor_branch(self) -> None:
        reynolds = 1200.0
        expected = 64.0 / reynolds
        actual = self.study.darcy_friction_factor(
            reynolds=reynolds,
            roughness_m=3.0e-5,
            diameter_m=1.2,
        )
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-12))


if __name__ == "__main__":
    unittest.main()
