# Ariadne Documentation

This directory contains detailed documentation for the Ariadne root system analysis software.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Scientific Methods](scientific-methods.md) | Pareto optimality calculations, formulas, and academic references |
| [Output Fields Reference](output-fields.md) | Complete reference for all CSV output fields with units and interpretation |

## Quick Links

- **Main README**: [../README.md](../README.md) - Installation and usage instructions
- **GitHub Repository**: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne
- **PyPI Package**: https://pypi.org/project/ariadne-roots/

## For Scientists

If you're using Ariadne for research and need to cite the underlying methods:

1. See [Scientific Methods](scientific-methods.md) for the mathematical foundations and primary references
2. The key papers are:
   - Chandrasekhar & Navlakha (2019) for Pareto optimality in biological networks
   - Conn et al. (2017) for network design principles in plant architectures

## For Developers

- Source code: `src/ariadne_roots/`
- Key modules:
  - `quantify.py` - Root trait calculations and analysis
  - `pareto_functions.py` - Pareto optimality algorithms
- Tests: `tests/` directory
- OpenSpec specifications: `openspec/` directory