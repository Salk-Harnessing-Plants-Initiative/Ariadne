# Ariadne
🌱 is a small software package for analyzing images of _Arabidopsis thaliana_ roots.

📷 It features a GUI for semi-automated image segmentation

<img src="assets/color-final.gif" width="250" height="250">

⏰ with support for time-series GIFs

<img src="assets/early-final.gif" width="250" height="250">

☠️ that creates dynamic 2D skeleton graphs of the root system architecture (RSA).

🔍 It's designed specifically to handle complex, messy, and highly-branched root systems well — the same situations in which current methods fail.

📊 It also includes some (very cool) algorithms for analyzing those skeletons, which were mostly developed by other (very cool) people<sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup>. The focus is on measuring cost-performance trade-offs and Pareto optimality in RSA networks.

⚠️ This is very much a work-in-progress! These are custom scripts written for a small, ongoing research project — so all code is provided as-is.

🔨 That said, if you're interested in tinkering with the code, enjoy! PRs are always welcome. And please reach out with any comments, ideas, suggestions, or feedback.

## Installation

Ariadne is installed as a Python package called `ariadne-roots`. We recommend using a package manager and creating an isolated environment for `ariadne-roots` and its dependencies. Our recommended package manager is Mamba. Follow the instructions to install [Miniforge3](https://github.com/conda-forge/miniforge).

You can find the latest version of `ariadne-roots` on the [Releases](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases) page.

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
    pip install ariadne-roots
    ```

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
4. **Trace the first root:**
    - Start tracing the entire primary root first (it should appear green).
    - To save time, place a dot on each region where a lateral root is emitted.
5. **Save the traced root:**
    - When the first root is fully traced, click on the “Save” button on the left-hand menu of Ariadne or press “g” on your keyboard.
    - A new window will pop up asking for the plant ID. For the first plant, enter “A”.
        - Each time you click on “Save”, a .json file will be saved in the folder at the location of Location_1 (see above).
6. **Trace additional roots:**
    - When you are done tracing the first root, click on the “Change root” button on the left-hand menu of Ariadne.
    - Select a new plant ID, like “B”, to trace the second root.
    - Continue tracing each root on your image following these steps.
7. **Finish tracing:**
    - When you have traced all roots on your image, click on “Change root” and repeat from “Step 3” above for any new images.

### Analyze with Ariadne

1. **Organize your files:**
    - Gather all the .json files stored in “location_1” into a new folder named “OUTPUT_JSON” (referred to as “location_2” later on).
    - Create a folder named “RESULTS” (referred to as “location_3”).
    - Create a new folder named “Output”.
2. **Prepare for analysis:**
    - Close Ariadne but keep the terminal open.
    - Follow the instructions in step 2 above to set up the terminal.
3. **Run the analysis:**
    - Click on “Analyze” in Ariadne.

    <img src="assets/Welcome.png" width="400" height="250">

    - Select the .json files to analyze from “location_2”.
    - Then select “location_3” for the output.
    - The software will analyze all the selected .json files.

### Results

- In the “location_3” folder, you will find:
    - A graph for each root showing the Pareto optimality.
    - A .csv file storing all the RSA traits for each root.

The RSA traits included in the CSV are

- **Material cost:** Total root length
- **Wiring cost:** Sum of the length from the hypocotyl to each root tip (Pareto related trait)
- **Alpha:** Trade-off value between growth and transport efficiency (Pareto related trait)
- **Scaling distance from the front:** Pareto optimality value (Pareto related trait)
- **Material cost (random):** Random total root length
- **Wiring cost (random):** Random sum of the length from the hypocotyl to each root tip (Pareto related trait)
- **Alpha (random):** Random trade-off value between growth and transport efficiency (Pareto related trait)
- **Scaling distance from the front (random):** Random Pareto optimality value (Pareto related trait)
- **Mean LR lengths:** Average length of all lateral roots
- **Median LR lengths:** Median length of all lateral roots
- **Mean LR angles:** Average lateral root set point angles
- **Median LR angles:** Median lateral root set point angles
- **Mean LR minimal distances:** Average Euclidean distance between each lateral root tip and its insertion on the primary root for all lateral roots
- **Median LR minimal distances:** Median Euclidean distance between each lateral root tip and its insertion on the primary root for all lateral roots
- **Sum LR minimal distances:** Sum of the Euclidean distances between each lateral root tip and its insertion on the primary root for all lateral roots
- **PR minimal length:** Euclidean distance from the hypocotyl to the primary root tip
- **PR length:** Length of the primary root
- **LR count:** Number of lateral roots
- **LR lengths:** Length of each individual lateral root
- **LR angles:** Lateral root set point angle of each individual lateral root
- **LR minimal distance:** Euclidean distance between each lateral root tip and its insertion on the primary root for each lateral root
- **LR density:** Number of lateral roots divided by primary root length, multiplied by 100
- **Total minimal distance:** Sum of LR minimal distances plus PR minimal length
- **Material/Total Distance Ratio:** Total root length divided by total minimal distance



##### Keybinds
* `Left-click`: place/select node. To pan, hold `Alt` or `Ctrl` and drag
* `t`: toggle skeleton visibility (default: on)
* `e`: next frame (GIFs only)
* `q`: previous frame (GIFs only)
* `r`: toggle proximity override. By default, clicking on or near an existing node will select it. When this override is on, a new node will be placed instead. Useful for finer control in crowded areas (default: off)
* `i`: toggle insertion mode. By default, new nodes extend a branch (i.e., have a degree of 1). Alternatively, use insertion mode to intercalate a new node between 2 existing ones. Useful for handling emering lateral roots in regions you have already segmented (default: off)
* `g`: Save output file
* `d`: Delete currently selected node(s)
* `c`: Erase the current tree and ask for a new plant ID
* `Ctrl-Z`: Undo last action


## Contributing
Follow these steps to set up your development environment and start making contributions to the project.

1. **Navigate to the desired directory:**
    Change directories to where you would like the repository to be downloaded:
    ```sh
    cd /path/on/computer/for/repos
    ```

2. **Clone the repository:**
    ```sh
    git clone https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne.git
    ```

3. **Navigate to the root of the cloned repository:**
    ```sh
    cd Ariadne
    ```

4. **Create a development environment:**
    This will install the necessary dependencies and the `ariadne-roots` package in editable mode:
    ```sh
    mamba env create -f environment.yaml
    ```

5. **Activate the development environment:**
    ```sh
    mamba activate ariadne-dev
    ```

6. **Create a branch for your changes:**
    Before making any changes, create a new branch:
    ```sh
    git checkout -b your-branch-name
    ```


## Contributors

- Kian Faizi
- Matt Platre
- Elizabeth Berrigan

## Contact

For any questions or further information, please contact:

- **Matt Platre:** [mattplatre@gmail.com](mailto:mattplatre@gmail.com)


## References
<b id="f1">1.</b> Chandrasekhar, Arjun, and Navlakha, Saket. "Neural arbors are Pareto optimal." _Proceedings of the Royal Society B_ 286.1902 (2019): 20182727. https://doi.org/10.1098/rspb.2018.2727 [↩](#a1)

<b id="f2">2.</b> Conn, Adam, et al. "High-resolution laser scanning reveals plant architectures that reflect universal network design principles." _Cell Systems_ 5.1 (2017): 53-62. https://doi.org/10.1016/j.cels.2017.06.017 [↩](#a2)