# GitHub Issue: Modular Cost Term Architecture

> **Note:** Create this issue manually at https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/issues/new

**Title:** Refactor: Modular cost term architecture for extensible Pareto analysis

---

## Summary

The current Pareto analysis implementation has ~340 lines of code duplicated between 2D and 3D versions, making it difficult to add new cost terms. This issue proposes a refactor to create a modular, extensible architecture.

## Problem

### Current Architecture Issues

1. **Massive Code Duplication** (~92% overlap between 2D and 3D)
   - `graph_costs` vs `graph_costs_3d_path_tortuosity`: 95% identical
   - `pareto_steiner_fast` vs `pareto_steiner_fast_3d_path_tortuosity`: 95% identical
   - `pareto_front` vs `pareto_front_3d_path_tortuosity`: 90% identical

2. **Cost Terms Tightly Coupled to BFS Traversal**
   - Cannot compute new cost terms without duplicating entire BFS algorithm
   - Each cost term embedded in traversal logic

3. **Parameter Space Explosion**
   - 2D: `alpha` parameter
   - 3D: `alpha, beta` parameters
   - 4D: `alpha, beta, gamma` parameters (combinatorial complexity)

### Adding a New Cost Term Today

To add a 4th cost term (e.g., "root depth", "branching angle variance"), you'd need:
- Create `graph_costs_4d_*` (~95 lines, copy of existing)
- Create `pareto_cost_4d_*` (~15 lines)
- Create `pareto_steiner_fast_4d_*` (~223 lines, copy of existing)
- Create `pareto_front_4d_*` (~50 lines)
- Update all callers in `quantify.py` and `main.py`

**Total: ~380 lines of new code, ~92% copy-paste**

## Proposed Solution

### CostTerm Abstraction

```python
from typing import Protocol, Dict, List
import networkx as nx

class CostTerm(Protocol):
    """Protocol for pluggable cost terms in Pareto analysis."""

    name: str
    minimize: bool  # True for costs to minimize, False for benefits to maximize

    def compute_for_graph(
        self,
        G: nx.Graph,
        traversal_data: Dict,  # BFS results: distances, paths, etc.
        critical_nodes: List[int] | None = None
    ) -> float:
        """Compute aggregate cost for the entire graph."""
        ...

    def compute_incremental(
        self,
        edge: tuple[int, int],
        graph_context: Dict
    ) -> float:
        """Compute cost contribution for a candidate edge (for greedy algorithm)."""
        ...
```

### Built-in Cost Terms

```python
class RootLengthTerm(CostTerm):
    """Total wiring cost (sum of edge lengths)."""
    name = "total_root_length"
    minimize = True

class TravelDistanceTerm(CostTerm):
    """Transport cost (sum of distances to base)."""
    name = "total_travel_distance"
    minimize = True

class PathTortuosityTerm(CostTerm):
    """Path coverage (sum of tortuosity ratios)."""
    name = "total_path_coverage"
    minimize = False  # Higher is better
```

### Unified Functions

```python
def graph_costs(
    G: nx.Graph,
    cost_terms: List[CostTerm],
    critical_nodes: List[int] | None = None
) -> Dict[str, float]:
    """Compute all cost terms in a single BFS traversal."""
    traversal_data = _bfs_traverse(G)  # Single traversal
    return {
        term.name: term.compute_for_graph(G, traversal_data, critical_nodes)
        for term in cost_terms
    }

def pareto_cost(
    costs: Dict[str, float],
    weights: Dict[str, float],
    terms: List[CostTerm]
) -> float:
    """Aggregate costs with arbitrary weighting."""
    total = 0.0
    for term in terms:
        sign = 1 if term.minimize else -1
        total += sign * weights.get(term.name, 0) * costs[term.name]
    return total

def pareto_steiner_fast(
    G: nx.Graph,
    cost_terms: List[CostTerm],
    weights: Dict[str, float]
) -> nx.Graph:
    """Single algorithm for any cost function."""
    # Uses cost_terms[i].compute_incremental() for greedy selection
    ...

def pareto_front(
    G: nx.Graph,
    cost_terms: List[CostTerm],
    weight_space: WeightSpace  # Abstraction for parameter sampling
) -> Dict[tuple, List[float]]:
    """Compute Pareto front for any number of cost terms."""
    ...
```

### Adding a New Cost Term After Refactor

```python
class RootDepthTerm(CostTerm):
    """Maximum depth from base to any tip."""
    name = "root_depth"
    minimize = True  # or False, depending on research question

    def compute_for_graph(self, G, traversal_data, critical_nodes=None):
        return max(traversal_data["distances_to_base"].values())

    def compute_incremental(self, edge, graph_context):
        return graph_context["new_depth"]
```

**Total: ~30-40 lines of new code, 0% copy-paste**

## Implementation Plan

### Phase 1: Extract BFS Traversal (Est. 2-3 days)
- [ ] Create `_bfs_traverse()` function returning traversal data dict
- [ ] Refactor `graph_costs()` to use shared traversal
- [ ] Add tests for traversal correctness

### Phase 2: Cost Term Protocol (Est. 2-3 days)
- [ ] Define `CostTerm` protocol
- [ ] Implement `RootLengthTerm`, `TravelDistanceTerm`, `PathTortuosityTerm`
- [ ] Refactor `graph_costs()` to use protocol
- [ ] Remove `graph_costs_3d_path_tortuosity()` (~95 lines deleted)

### Phase 3: Generalize Cost Aggregation (Est. 1-2 days)
- [ ] Create flexible `pareto_cost()` with dict-based weights
- [ ] Remove `pareto_cost_3d_path_tortuosity()` (~35 lines deleted)
- [ ] Add constraint validation

### Phase 4: Unified Steiner Algorithm (Est. 2-3 days)
- [ ] Parameterize `pareto_steiner_fast()` with cost callback
- [ ] Remove `pareto_steiner_fast_3d_path_tortuosity()` (~223 lines deleted)
- [ ] Add tests for algorithm equivalence

### Phase 5: Abstract Parameter Space (Est. 1-2 days)
- [ ] Create `WeightSpace` abstraction for sampling
- [ ] Unify `pareto_front()` for any dimension
- [ ] Remove `pareto_front_3d_path_tortuosity()` (~49 lines deleted)

## Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Lines to add new cost term | ~380 | ~40 | **90% reduction** |
| Code duplication | ~340 lines | 0 | **340 lines deleted** |
| Maintenance burden | 2x (parallel functions) | 1x | **50% reduction** |

## References

- Related PR: #19 (3D path tortuosity feature)
- Related change: `fix-3d-pareto-robustness` (robustness fixes for PR #19)
- Files affected:
  - `src/ariadne_roots/pareto_functions.py` (major refactor)
  - `src/ariadne_roots/quantify.py` (update callers)
  - `src/ariadne_roots/main.py` (update callers)
  - `tests/` (new tests, update existing)

## Acceptance Criteria

- [ ] Single `graph_costs()` function works for 2D and 3D analysis
- [ ] Single `pareto_steiner_fast()` function works for any cost combination
- [ ] Adding a new cost term requires <50 lines of code
- [ ] All existing tests pass
- [ ] No regression in analysis output values
- [ ] Code coverage maintained at ≥80%

## Labels

- `enhancement`
- `refactor`
- `architecture`