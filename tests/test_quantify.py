import pytest
import json
import numpy as np
import numpy.testing as npt

from math import isclose
from networkx.readwrite import json_graph

from ariadne_roots.quantify import analyze


def test_analyze(
    plantB_day11_json,
    plantB_day11_lr_lengths,
    plantB_day11_lr_angles,
    plantB_day11_lr_minimal_lengths,
):
    # load the json file
    with open(plantB_day11_json, mode="r") as h:
        data = json.load(h)
        # convert to networkx graph
        graph = json_graph.adjacency_graph(data)

        # perform analysis
        results, front, randoms = analyze(graph)

        # check the results
        assert len(results) == 31  # 31 features
        # Random values are not tested here
        # Scalar assertions
        assert isclose(results["Total root length"], 13196.30945, rel_tol=1e-8)
        assert isclose(results["Travel distance"], 34709.9406, rel_tol=1e-8)
        assert isclose(results["alpha"], 0, rel_tol=1e-8)
        assert isclose(results["scaling distance to front"], 1.067228823, rel_tol=1e-8)
        assert isclose(results["PR length"], 3610.664228, rel_tol=1e-8)
        assert isclose(results["PR_minimal_length"], 3459.128503, rel_tol=1e-8)
        assert isclose(results["Basal Zone length"], 0, rel_tol=1e-8)
        assert isclose(results["Branched Zone length"], 1869.271258, rel_tol=1e-8)
        assert isclose(results["Apical Zone length"], 1741.39297, rel_tol=1e-8)
        assert isclose(results["Mean LR lengths"], 399.4018841, rel_tol=1e-8)
        assert isclose(results["Mean LR minimal lengths"], 384.593032, rel_tol=1e-8)
        assert isclose(results["Median LR lengths"], 219.7926545, rel_tol=1e-8)
        assert isclose(results["Median LR minimal lengths"], 209.9816672, rel_tol=1e-8)
        assert isclose(results["sum LR minimal lengths"], 9230.232768, rel_tol=1e-8)
        assert isclose(results["Mean LR angles"], 61.27733707, rel_tol=1e-8)
        assert isclose(results["Median LR angles"], 59.46912539, rel_tol=1e-8)
        assert results["LR count"] == 24
        assert isclose(results["LR density"], 0.006646976, rel_tol=1e-6)
        assert isclose(results["Branched Zone density"], 0.012839228, rel_tol=1e-8)
        assert isclose(results["Barycenter x displacement"], 95.82352941, rel_tol=1e-8)
        assert isclose(results["Barycenter y displacement"], 1106.823529, rel_tol=1e-8)
        assert isclose(results["Total minimal Distance"], 12689.36127, rel_tol=1e-8)
        assert isclose(results["Tortuosity"], 1.039950646, rel_tol=1e-8)
        assert isclose(results["Convex Hull Area"], 1039998.5, rel_tol=1e-8)
        # Assertions for arrays
        npt.assert_allclose(results["LR lengths"], plantB_day11_lr_lengths, rtol=1e-8)
        npt.assert_allclose(results["LR angles"], plantB_day11_lr_angles, rtol=1e-8)
        npt.assert_allclose(
            results["LR minimal lengths"], plantB_day11_lr_minimal_lengths, rtol=1e-8
        )

        # Check the front
        assert len(front) == 101
        # When alpha is 0 the satellite tree is used so the total_root_length is the same as the total_travel_distance
        npt.assert_allclose(
            front.get(np.float64(0.0)),
            [32523.428762791922, 32523.428762791922],
            rtol=1e-8,
        )
        assert isclose(
            front.get(np.float64(0.0))[0], front.get(np.float64(0.0))[1], rel_tol=1e-8
        )

        min_root_length = min(front.values(), key=lambda x: x[0])[0]
        max_root_length = max(front.values(), key=lambda x: x[0])[0]
        min_travel_distance = min(front.values(), key=lambda x: x[1])[1]
        max_travel_distance = max(front.values(), key=lambda x: x[1])[1]
        # When alpha is 0, the total_root_length is maximal and the total_travel_distance is minimal
        assert max_root_length == front.get(np.float64(0.0))[0]
        assert min_travel_distance == front.get(np.float64(0.0))[1]
        # When alpha is 1, the total_root_length is minimal and the total_travel_distance is maximal
        assert min_root_length == front.get(np.float64(1.0))[0]
        assert max_travel_distance == front.get(np.float64(1.0))[1]
        # alpha 0.5 is the middle of the front
        assert isclose(
            front.get(np.float64(0.5))[0], 5196.958333735241, rel_tol=1e-8
        )  # total_root_length
        assert isclose(
            front.get(np.float64(0.5))[1], 34690.010682440174, rel_tol=1e-8
        )  # total_travel_distance
