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

Ariadne is installed as a Python package called `ariadne-roots`. We recommend installing a package manager and creating an isolated environment for `ariadne-roots` and its dependencies. Our recommended environment and package manager is Mamba. Follow the instructions to install (Miniforge3)[https://github.com/conda-forge/miniforge].

You can find the latest version of `ariadne-roots` in the (Releases)[https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases] page.

To make an isolated environment use
```
mamba create --name ariadne python=3.11
```

then install `ariadne-roots` using `pip`
```
pip install ariadne-roots
```

## Usage

Activate your environment using

```
mamba activate ariadne
```

Open the GUI using

```
python main.py
```
<img src="assets/Python_main.png" width="250" height="100">


### Trace with Ariadne

-	Click on “Trace” to trace Roots.
-	The window below should be opened now:

<img src="assets/Trace_Menu.png" width="450" height="450">

-	Click on “Import image file”
-	Select the image to trace the roots
-	Trace the root number 1. 
        * Caution start to trace the entire primary root first (should appear green). To gain time place a dot on each region where a lateral root is emitted. 
-	When the first root is all traced click on “Save” button on the left-hand menu of Ariadne or tap “g” on your keyboard.
-	A new window will pop up asking for the plant ID, for the first plant say “A”
        * Every time you’ll click on “Save” a .json file will be saved in the folder at the location of Location_1 (see above).
-	When you are done tracing the first root, click on “change root” button on the left-hand menu of Ariadne
-	Select a new plant ID, like “B” for example to trace the root number 2.
-	Continue like that until you traced every root on your image. 
-	When you are done tracing all roots on your image click on “change root” and restart from “Step 3” indicated above.

### Analyze with Ariadne
-	Ideally, gather all the .json stored in ”location_1” into a new Folder named “OUTPUT_JSON” for example, refereed as “location_2” later on.
-	Create a file named for example named “RESULTS”, refereed as “location_3”
-	Create a new folder named Output. 
-	Close Ariadne but keep the terminal open.
-	On the terminal do the step 2, see above.
-	Click on analyze 

<img src="assets/Welcome.png" width="400" height="250">

-	Select the .json file to analyze which are stored at the  “location_2”.
-	Then select the location_3
-	The software is now running to analyze all the .json files selected. 
### Results
-	In the location_3 folder, you’ll find a graph for each root where the Pareto optimality will be represented.
-	You’ll find a .csv file where all the RSA traits will be store for each root.
-	Each column contains the calculation for:
*	Material cost = total root length
*	Wiring cost = Sum of the length from the hypocotyl to each root tip (pareto related trait)
*	Alpha = trade off value between growth and transport efficiency (pareto related trait)
*	Scaling distance from the from the front =Pareto optimality value(pareto related trait)
*	Material cost (random) = random total root length
*	Wiring cost (random) = random Sum of the length from the hypocotyl to each root tip (pareto related trait)
*	Alpha (random) = random trade off value between growth and transport efficiency (pareto related trait)
*	Scaling distance from the from the front (random) = random Pareto optimality value(pareto related trait)
*	Mean LR lengths = average of the length of all lateral roots
*	Median LR lengths = Median of the length of all lateral roots
*	Mean LR angles = average of lateral root set point angles 
*	Median LR angles = Median of lateral root set point angles
*	Mean LR minimal distances = average of the Euclidian distance between each lateral root tips to their insertion on the primary root for all the lateral roots.
*	Median LR minimal distances = median of the Euclidian distance between each lateral root tips to their insertion on the primary root for all the lateral roots.
*	Sum LR minimal distances = Sum of the Euclidian distance between each lateral root tips to their insertion on the primary root for all the lateral roots.
*	PR minimal length = Euclidean distance between the hypocotyl to the primary root tip.
*	PR length = length of the lateral root
*	LR count = number of lateral root
*	LR lengths = length of each individual lateral root
*	LR angles = lateral root set point angle of each individual lateral root
*	LR minimal distance = Euclidian distance between each lateral root tips to their insertion on the primary root for each lateral roots
*	LR density = number of lateral root divided by PR length * 100
*	Total minimal distance = Sum LR minimal distances plus PR minimal length
*	Material/TotalDistance Ratio = Total root length / Total minimal distance



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


## Contributers


## Contact



## References
<b id="f1">1.</b> Chandrasekhar, Arjun, and Navlakha, Saket. "Neural arbors are Pareto optimal." _Proceedings of the Royal Society B_ 286.1902 (2019): 20182727. https://doi.org/10.1098/rspb.2018.2727 [↩](#a1)

<b id="f2">2.</b> Conn, Adam, et al. "High-resolution laser scanning reveals plant architectures that reflect universal network design principles." _Cell Systems_ 5.1 (2017): 53-62. https://doi.org/10.1016/j.cels.2017.06.017 [↩](#a2)