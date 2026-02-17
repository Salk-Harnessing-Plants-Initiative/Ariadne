# Ariadne

[![Stable version](https://img.shields.io/pypi/v/ariadne-roots?label=stable "Stable version")](https://pypi.org/project/ariadne-roots/)
[![Latest pre-release](https://img.shields.io/github/v/release/Salk-Harnessing-Plants-Initiative/Ariadne?include_prereleases&label=pre-release)](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases)


🌱 is a small software package for analyzing images of _Arabidopsis thaliana_ roots.

📷 It features a GUI for semi-automated image segmentation

<img src="assets/color-final.gif" width="250" height="250">

⏰ with support for time-series GIFs

<img src="assets/early-final.gif" width="250" height="250">

☠️ that creates dynamic 2D skeleton graphs of the root system architecture (RSA).

🔍 It's designed specifically to handle complex, messy, and highly-branched root systems well — the same situations in which current methods fail.

📊 It also includes some (very cool) algorithms for analyzing those skeletons, which were mostly developed by other (very cool) people<sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup>. The focus is on measuring cost-performance trade-offs and Pareto optimality in RSA networks.

⚠️ This is very much a work-in-progress! These are custom scripts written for an ongoing research project — so all code is provided as-is.

🔨 That said, if you're interested in tinkering with the code, enjoy! PRs are always welcome. And please reach out with any comments, ideas, suggestions, or feedback.

## Documentation

📚 **Detailed documentation for scientists and developers:**

| Document | Description |
|----------|-------------|
| [Scientific Methods](docs/scientific-methods.md) | Pareto optimality calculations, mathematical formulas, and academic references |
| [Output Fields Reference](docs/output-fields.md) | Complete reference for all CSV output fields with units and interpretation |

For citing the underlying methods, see the [References](#references) section or the [Scientific Methods](docs/scientific-methods.md) documentation.

## Installation

Ariadne is installed as a Python package called `ariadne-roots`. We recommend using a package manager and creating an isolated environment for `ariadne-roots` and its dependencies.
You can find the latest version of `ariadne-roots` on the [Releases](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases) page.


## Installation (Users)

We recommend installing Ariadne in an isolated environment using `uv`.  You can install it with [uv](https://docs.astral.sh/uv/) to keep your environment clean and reproducible.

### Prerequisites

The GUI requires **tkinter**, which is part of Python's standard library:

- **uv (recommended)**: tkinter is included automatically with uv's managed Python installations
- **macOS (system Python via Homebrew)**: `brew install python-tk@3.12` (only if not using uv)
- **Ubuntu/Debian (system Python)**: `sudo apt-get install python3-tk` (only if not using uv)
- **Windows (system Python)**: tkinter is typically included with standard Python installations
- **conda/mamba**: tkinter is included automatically

To verify tkinter is available: `python -c "import tkinter"`

**Note:** If you use `uv` to manage Python (recommended), tkinter is already included and requires no separate installation.

There are three main ways to install and run Ariadne:

---

### Option 1. Local Environment

This creates a local `.venv` folder to hold Ariadne and its dependencies.

```sh
# Create a local environment with pip + setuptools pre-seeded
uv venv --seed .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Activate it (Windows PowerShell)
.venv\Scripts\activate

# Install Ariadne
uv pip install ariadne-roots
```

Then run the GUI:

```sh
ariadne-trace
```

---

### Option 2. One-liner Install & Run (no manual environment necessary)

You can also run Ariadne directly with `uvx`, which installs it into an isolated cache and exposes the CLI:

```sh
uvx ariadne-trace
```

This will launch the GUI without needing to set up or activate a venv manually.

---

### Option 3. Project-Based Workflow (for developers/power users)

This approach creates a dedicated project for using Ariadne with `uv init` and `uv add`:

```sh
# Create a new project directory
uv init ariadne-project
cd ariadne-project

# Add Ariadne as a dependency (creates .venv automatically)
uv add ariadne-roots

# Run the GUI
uv run ariadne-trace
```

This is ideal if you want to:
- Keep Ariadne alongside other analysis tools in a project
- Lock dependencies with `uv.lock` for reproducibility
- Manage multiple environments for different analyses

---


## Usage

### If installed in a local environment (Option 1)
Activate the environment and run:

```sh
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
ariadne-trace
```

### If using the one-liner (Option 2)
Simply run:

```sh
uvx ariadne-trace
```

### If using project-based workflow (Option 3)
Run from your project directory:

```sh
cd ariadne-project
uv run ariadne-trace
```

### `conda` environment installation

Follow the instructions to install [Miniforge3](https://github.com/conda-forge/miniforge).

### Step-by-Step Installation

1. **Create an isolated environment:**
    ```sh
    mamba create --name ariadne python=3.11
    ```

2. **Activate your environment:**
    ```sh
    mamba activate ariadne
    ```

3. **Install `ariadne-roots` using pip:**
    ```sh
    pip install --pre ariadne-roots  # Use --pre to include pre-release versions
    ```
    - Omit the `--pre` flag if you only want to install stable releases.


## Usage

1. **Activate your environment:**
    ```sh
    mamba activate ariadne
    ```

2. **Open the GUI:**
    ```sh
    ariadne-trace
    ```


### Trace with Ariadne

1. **Click on “Trace”** to trace roots.
2. The following window should open:

    <img src="assets/Trace_Menu.png" width="450" height="450">

3. **Click on “Import image file”** and select the image to trace the roots.
4. **Select the zoom factor for your image** 
    - A window should popup asking for the zoom factor
    - Use the "Zoom in" and Zoom out" button to adjust the zoom needed to trace the root system with high precision
    - Click on "OK"
    - After this, any new image imported will be opened with the identical zoom factor
    - Remark: after closing Ariadne, the zoom factor will be canceled. Therefore, take note of the zoom factor used and reapply the same everytime when restarting Ariadne.
5. **Trace the first root:**
    - Start tracing the entire primary root first (it should appear green).
    - To save time, place a dot on each region where a lateral root is emitted.
6. **Save the traced root:**
    - When the first root is fully traced, click on the “Save” button on the left-hand menu of Ariadne or press “g” on your keyboard.
    - A new window will pop up asking for the plant ID. Tap any letter “A” or number "1".
        - Each time you click on “Save”, a .json file will be saved in the folder at the location of Location_1 (see above).
7. **Trace additional roots:**
    - When you are done tracing the first root, click on the “Change root” button on the left-hand menu of Ariadne.
    - Select a new plant ID, like “B”, to trace the second root.
    - Continue tracing each root on your image following these steps.
8. **Finish tracing:**
    - When you have traced all roots on your image, click on “Change root” and repeat from “Step 3” above for any new images.

### Analyze with Ariadne

1. **Organize your files:**
    - Gather all the .json files stored at the location where Ariadne has been installed into a new folder named "OUTPUT_JSON" (referred to as "location_1" later on).
    - Create a folder named "RESULTS" (referred to as "location_2").
    - Create a new folder named "Output".
2. **Prepare for analysis:**
    - Close Ariadne but keep the terminal open.
    - Follow the instructions in step 2 above to set up the terminal.
3. **Run the analysis:**
    - Click on "Analyze" in Ariadne.

    <img src="assets/Welcome.png" width="400" height="250">

    - **Set scaling parameters** (optional):
        - A dialog will appear asking you to configure measurement units
        - Enter the conversion factor (e.g., if 1 pixel = 2.5 mm, enter `1` for pixels and `2.5` for distance)
        - Select or enter the unit name (e.g., "mm", "cm", "µm")
        - Click "OK" to continue, or "Cancel" to use default (pixels)
    - **Select input files**:
        - Choose the .json files to analyze from "location_1"
        - An info dialog will confirm the number of files selected
    - **Select output folder**:
        - Choose "location_2" for the output
        - The software will analyze all selected files and save results
    - **Completion**:
        - A dialog will show where the results were saved (CSV report and Pareto plots)

### Results

- In the output folder you selected, you will find:
    - A Pareto optimality plot for each root (PNG format)
    - A timestamped CSV file (e.g., `report_20241110_153045.csv`) storing all RSA traits for each root

**Note on Units:** If you configured scaling during analysis, all length measurements in the CSV and plots will be in your specified units (e.g., mm, cm). Otherwise, measurements are in pixels.

The RSA traits included in the CSV are

- **Total root length:** Total root length
- **Travel distance:** Sum of the length from the hypocotyl to each root tip (Pareto related trait)
- **Alpha:** Trade-off value between growth and transport efficiency (Pareto related trait)
- **Scaling distance to front:** Pareto optimality value (Pareto related trait)
- **Total root length (random):** Random total root length
- **Travel distance (random):** Random sum of the length from the hypocotyl to each root tip (Pareto related trait)
- **Alpha (random):** Random trade-off value between growth and transport efficiency (Pareto related trait)
- **Scaling distance to front (random):** Random Pareto optimality value (Pareto related trait)
- **PR length:** Length of the primary root
- **PR minimal length:** Euclidean distance from the hypocotyl to the primary root tip
- **Basal zone length:** length from the hypocotyl to the insertion of the first lateral root along the primary root 
- **Branched zone length:** length from the insertion of the first lateral root to the insertion of the last lateral root along the primary root 
- **Apical zone length:** length from the last lateral root to the root tip along the primary root 
- **Mean LR lengths:** Average length of all lateral roots
- **Mean LR minimal distances:** Average Euclidean distance between each lateral root tip and its insertion on the primary root for all lateral roots
- **Median LR lengths:** Median length of all lateral roots
- **Median LR minimal distances:** Median Euclidean distance between each lateral root tip and its insertion on the primary root for all lateral roots
- **Sum LR minimal distances:** Sum of the Euclidean distances between each lateral root tip and its insertion on the primary root for all lateral roots
- **Mean LR angles:** Average lateral root set point angles
- **Median LR angles:** Median lateral root set point angles
- **LR count:** Number of lateral roots
- **LR density:** Number of lateral roots divided by primary root length
- **Branched zone density:** Number of lateral roots divided by Branched zone length
- **LR lengths:** Length of each individual lateral root
- **LR angles:** Lateral root set point angle of each individual lateral root
- **LR minimal distance:** Euclidean distance between each lateral root tip and its insertion on the primary root for each lateral root
- **Barycentre x displacement:** Vertical distance between the hypocotyl base to the barycenter of the convex hull
- **Barycentre y displacement:** Horizontal distance between the hypocotyl base to the barycenter of the convex hull
- **Total minimal distance:** Sum of LR minimal distances plus PR minimal length
- **Tortuosity (Material/Total Distance Ratio):** Total root length divided by total minimal distance

#### 3D Pareto Analysis Fields (Optional)

When **"Add path tortuosity to Pareto (3D, slower)"** is enabled during analysis, additional fields are computed that include path coverage as a third objective:

- **Path tortuosity:** Sum of tortuosity values for all root paths
- **alpha_3d, beta_3d, gamma_3d:** Interpolated Pareto weights (α + β + γ = 1)
- **epsilon_3d:** Multiplicative ε-indicator measuring distance from the 3D Pareto front
- **epsilon_3d_material/transport/coverage:** Individual ratio components showing which objective constrains optimality
- **Corner costs (Steiner/Satellite/Coverage):** Reference values for optimal architectures at each corner of the Pareto surface

For complete field descriptions, see the [Output Fields Reference](docs/output-fields.md).

##### Keybinds
* `Left-click`: place/select node. 
* `Ctrl`: Hold Ctrl to scroll through the image with the mouth
* `t`: toggle skeleton visibility (default: on)
* `e`: next frame (GIFs only)
* `q`: previous frame (GIFs only)
* `r`: toggle proximity override. By default, clicking on or near an existing node will select it. When this override is on, a new node will be placed instead. Useful for finer control in crowded areas (default: off)
* `i`: toggle insertion mode. By default, new nodes extend a branch (i.e., have a degree of 1). Alternatively, use insertion mode to intercalate a new node between 2 existing ones. Useful for handling emering lateral roots in regions you have already segmented (default: off)
* `g`: Save output file
* `d`: Delete currently selected node(s)
* `c`: Erase the current tree and ask for a new plant ID
* `+`: Zoom in
* `-`: Zoom out
* `Ctrl-Z`: Undo last action


## Contributing
Follow these steps to set up your development environment and start making contributions to the project.

1. **Navigate to the desired directory**

    Change directories to where you would like the repository to be downloaded
    ```sh
    cd /path/on/computer/for/repos
    ```

2. **Clone the repository**
    ```sh
    git clone https//github.com/Salk-Harnessing-Plants-Initiative/Ariadne.git
    ```

3. **Navigate to the root of the cloned repository**
    ```sh
    cd Ariadne
    ```

## 🛠️ For Developers

### Requirements
- [uv](https://github.com/astral-sh/uv) for dependency management
- Python 3.11+

### Setting Up a Development Environment

Clone the repository:

```bash
git clone https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne.git
cd Ariadne
```

## 🛠️ Development with uv

We use [uv](https://github.com/astral-sh/uv) for dependency management and tooling.
- This workflow is tested in GitHub Actions using `.github/workflows/test-dev.yml`.
- Python version is pinned to 3.12 in `.python-version` (CI tests 3.12 and 3.13).
- Dependencies are locked in `uv.lock` for reproducible builds.

### Quick Start

After cloning the repository, set up your development environment:

```bash
uv sync
```

This command:
- Reads `.python-version` to use Python 3.12 automatically
- Creates `.venv` (if it doesn't exist)
- Installs dependencies from the committed `uv.lock` file (reproducible!)
- Installs runtime dependencies plus the `dev` group (tests, linters, etc.)

**Important:** Always use `uv sync` (not `uv pip install`) to ensure you get the exact dependency versions from the lockfile.

---

### Running Commands

Use `uv run` to execute commands **inside the project environment** without manually activating `.venv`:

```bash
# Run tests with coverage
uv run pytest --cov=ariadne_roots --cov-report=term-missing

# Check code formatting
uv run black --check .

# Run linting
uv run ruff check .

# Run the CLI
uv run ariadne-trace
```

**Cross-platform:** `uv run` works on Linux, macOS, and Windows without needing venv activation.

---

### Updating Dependencies

To update dependencies, modify `pyproject.toml` then regenerate the lockfile:

```bash
# Update lockfile after changing dependencies
uv lock

# Sync environment with new lockfile
uv sync

# Commit both files
git add pyproject.toml uv.lock
git commit -m "Update dependencies"
```

**CI Integration:** Our CI uses `uv sync --frozen` to ensure the lockfile isn't modified during builds, catching any uncommitted dependency changes.

---

### Security & Dependency Scanning

We maintain secure dependencies through regular vulnerability scanning. To check for known vulnerabilities:

```bash
# Scan current dependencies for security issues
uvx pip-audit
```

**Best Practices:**
- Run `uvx pip-audit` before each release
- Check the lockfile regularly for outdated dependencies with known vulnerabilities
- Review [GitHub Security Advisories](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/security/advisories) for this repository

**Automated Monitoring:**
Consider enabling GitHub Dependabot to receive automated pull requests for dependency updates and security patches.

**Current Status:** No known vulnerabilities (last checked: November 2025)

---

### 3. Building artifacts
To build source and wheel distributions:

```bash
uv build
```

Artifacts will be created in the `dist/` directory.

---

### Alternative: install dev extras with pip
If you’re not using `uv`, you can still install everything with pip:

```bash
pip install -e ".[dev]"
```

This installs runtime + dev dependencies into your current environment.

---

### Instructions for `conda` environment

1. **Create a development environment**

    This will install the necessary dependencies and the `ariadne-roots` package in editable mode
    ```sh
    mamba create --name ariadne_dev python=3.11 # python 3.11, 3.12, 3.13 are tested in the CI
    ```

2. **Activate the development environment**
    ```sh
    mamba activate ariadne_dev
    ```

3. **Install dev dependencies and source code in editable mode**
    ```bash
    pip install -e ".[dev]"
    ```


## Development Rules
1. **Create a branch for your changes**

    Before making any changes, create a new branch
    ```sh
    git checkout -b your-branch-name
    ```

2. **Code**

    Make your changes. Please make sure your code is readable and documented.

    - The Google style is preferred.
    - Use docstrings with args and returns defined for each function.
    - Typing annotations are preferred.
    - Use comments to explain steps of calculations and algorithms.
    - Use consistent variable names.
        - Please use full words and not letters as variable names so that variables are readable.

3. **Commit often**

    Commit your changes frequently with short, descriptive messages. This helps track progress and makes it easier to identify issues.

    ```sh
    git add <changed_files>
    git commit -m "Short, descriptive commit message"
    ```

4. **Open a pull request**

    Before you make any changes, you can write a descriptive plan of what you intend to do and why.
    Once your changes are ready, push your branch to the remote repository. Provide a clear explanation of what you changed and why.

    ```sh
    git push origin your-branch-name
    ```

    - Go to the repository on GitHub.
    - Click on **Compare & pull request**.
    - Fill in the title and description of your pull request.
    - Click **Create pull request**.

5. **Test your changes**

    Ensure your changes pass all tests and do not break existing functionality.

6. **Request a review**

    In the pull request, request a review from the appropriate team members. Notify them via GitHub.

7. **Merge your changes to main**

    After your code passes review, merge your changes to the `main` branch.

    - Click **Merge pull request** on GitHub.
    - Confirm the merge.

8. **Delete your remote branch**

    Once your changes are merged, delete your remote branch to keep the repository clean.



## Releasing `ariadne-roots`

The GitHub Action workflow `.github/workflows/python-publish.yml` results in the package, `ariadne-roots`, being released at [PyPI](https://pypi.org/project/ariadne-roots/).

To release a new package, follow these instructions:

**Follow contributing instructions above**

1. **Make a new branch to record your changes**
    ```sh
    git checkout -b <your_name>/bump_version_to_<version>
    ```

2. **Modify version**

    The `pyproject.toml` file contains the information for the pip package. Incrementally increase the "version" with each release.

    **Semantic Versioning**

    Semantic versioning (SemVer) is a versioning system that uses the format:
    `MAJOR.MINOR.PATCH`

    - **MAJOR:** Increase when you make incompatible API changes.
    - **MINOR:** Increase when you add functionality in a backward-compatible manner.
    - **PATCH:** Increase when you make backward-compatible bug fixes.

    For example:

    - If the current version is `1.2.3`:
    - A breaking change would result in `2.0.0`.
    - Adding a new feature would result in `1.3.0`.
    - Fixing a bug would result in `1.2.4`.

    Learn more about the rules of semantic versioning [here](https://semver.org).

3. **Commit changes**

    After making the required modifications, commit your changes:
    ```sh
    git add pyproject.toml
    git commit -m "Bump version to <version>"
    git push origin <your_name>/bump_version_to_<version>
    ```

4. **Open a pull request**

    1. Go to the repository on GitHub.
    2. You should see a banner prompting you to compare & create a pull request for your branch. Click it.
    3. Fill in the pull request title and description. For example:
        - **Title:** Bump version to `<version>`
        - **Description:** "This PR updates the version to `<version>` for release."
    4. Click **Create pull request**.

5. **Request a review**

    After creating the pull request, in the right-hand sidebar, click on **Reviewers** and select the appropriate reviewer(s). Notify the reviewer(s) via GitHub.

6. **Merge your changes to `main` after review**

    Once the reviewer approves your pull request, merge it into the `main` branch.

7. **Release to trigger the workflow**

    1. Go to the [release page](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases).
    2. Draft a new release:
        - Create a new tag with the version number you used in the repository.
        - Have GitHub draft the release notes to include all the changes since the last release.
        - Modify the release name to include `ariadne-roots`, so that it says `ariadne-roots v<version>` like the rest.
    3. Please ask for your release to be reviewed before releasing.

8. **Verify the release**

    Check [PyPI](https://pypi.org/project/ariadne-roots/#history) and the GitHub Actions of our repository to make sure the pip package was created and published successfully.
    - You should see the latest release with the correct version number at pypi.org.
    - The Github Actions should have green checkmarks and not red X's associated with your release.

## Contributors

- Kian Faizi
- Matthieu Platre
- Elizabeth Berrigan

## Contact

For any questions or further information, please contact:

- **Matthieu Platre:** [matthieu.platre@inrae.fr](mailto:matthieu.platre@inrae.fr)


## References
<b id="f1">1.</b> Chandrasekhar, Arjun, and Navlakha, Saket. "Neural arbors are Pareto optimal." _Proceedings of the Royal Society B_ 286.1902 (2019): 20182727. https://doi.org/10.1098/rspb.2018.2727 [↩](#a1)

<b id="f2">2.</b> Conn, Adam, et al. "High-resolution laser scanning reveals plant architectures that reflect universal network design principles." _Cell Systems_ 5.1 (2017): 53-62. https://doi.org/10.1016/j.cels.2017.06.017 [↩](#a2)
