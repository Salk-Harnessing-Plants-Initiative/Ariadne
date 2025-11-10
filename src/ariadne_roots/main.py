"""ARIADNE

A GUI for segmenting root images from Arabidopsis seedlings grown on agar plates.

@kfaizi on GitHub

Todo:
if imported file is not a GIF, block next/prev buttons
try:except for dialog errors?
easier selection of nearby points
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import copy
import networkx as nx
import json
import logging

from pathlib import Path
from queue import Queue
from collections import deque
from PIL import Image, ImageTk, ImageSequence
from datetime import datetime
from networkx.readwrite import json_graph

from ariadne_roots import quantify, config, scaling


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class StartupUI:
    """Startup window interface."""

    def __init__(self, base):
        self.base = base
        self.base.geometry("350x200")

        # master frame
        self.frame = tk.Frame(self.base)
        self.frame.pack(side="top", fill="both", expand=True)

        # salutation
        self.title_frame = tk.Frame(self.frame)
        self.title_frame.pack()

        self.title_label = tk.Label(self.frame, text="Welcome to Ariadne!")
        self.title_label.pack(side="top", fill="both", expand=True)

        # buttons
        self.trace_button = tk.Button(self.frame, text="Trace", command=self.to_trace)
        self.analyze_button = tk.Button(
            self.frame, text="Analyze", command=self.to_analyze
        )

        self.trace_button.pack(side="top", fill="both", expand=True)
        self.analyze_button.pack(side="bottom", fill="both", expand=True)

    def to_trace(self):
        """Swap frames to tracing mode."""
        self.frame.destroy()
        TracerUI(self.base)

    def to_analyze(self):
        """Swap frames to analysis mode."""
        self.frame.destroy()
        AnalyzerUI(self.base)


class TracerUI(tk.Frame):
    """Tracing mode interface."""

    def __init__(self, base):
        super().__init__(base)
        self.base = base
        self.base.geometry("1750x1600")
        self.base.title("Ariadne: Trace")
        # Initialize scale factor and the flag for first image import
        self.scale_factor = 1
        self.first_image_imported = False  # Flag to check first image import

        # master frame
        self.frame = tk.Frame(self.base)
        self.frame.pack(side="top", fill="both", expand=True)

        # filename titlebar
        self.title_frame = tk.Frame(self.frame)
        self.title_label = tk.Label(self.title_frame, text="Tracing")
        self.title_label.pack()

        # left-hand menu
        self.menu = tk.Frame(self.frame, width=175, bg="skyblue")
        self.menu.pack(side="top", fill="both")

        self.button_import = tk.Button(
            self.menu, text="Import image file", command=self.import_image
        )
        self.button_next = tk.Button(
            self.menu, text="Next day (e)", command=None, state="disabled"
        )
        self.button_prev = tk.Button(
            self.menu, text="Prev day (q)", command=None, state="disabled"
        )
        self.button_override = tk.Button(
            self.menu, text="Override (r)", command=None, state="disabled"
        )
        self.button_insert = tk.Button(
            self.menu, text="Insert (i)", command=None, state="disabled"
        )
        self.button_undo = tk.Button(
            self.menu, text="Undo (Ctrl-z)", command=None, state="disabled"
        )
        self.button_save = tk.Button(
            self.menu, text="Save (g)", command=None, state="disabled"
        )
        self.button_show = tk.Button(
            self.menu, text="Show/hide tree (t)", command=None, state="disabled"
        )
        self.button_change_root = tk.Button(
            self.menu, text="Change Root (c)", command=None, state="disabled"
        )
        self.button_zoom_in = tk.Button(
            self.menu, text="Zoom In (+)", command=None, state="disabled"
        )
        self.button_zoom_out = tk.Button(
            self.menu, text="Zoom Out (-)", command=None, state="disabled"
        )
        self.button_import.pack(fill="x", side="top")
        self.button_prev.pack(fill="x", side="top")
        self.button_next.pack(fill="x", side="top")
        self.button_override.pack(fill="x", side="top")
        self.button_insert.pack(fill="x", side="top")
        self.button_undo.pack(fill="x", side="top")
        self.button_save.pack(fill="x", side="top")
        self.button_show.pack(fill="x", side="top")
        self.button_change_root.pack(fill="x", side="top")
        self.button_zoom_in.pack(fill="x", side="top")
        self.button_zoom_out.pack(fill="x", side="top")

        # image canvas
        self.canvas = tk.Canvas(self.frame, width=600, height=700, bg="gray")
        self.img = None

        # useful flags
        self.prox_override = False  # tracks whether proximity override is on
        self.inserting = False  # tracks whether insertion mode is on
        self.tree_flag = "normal"  # used for hiding/showing tree's edges
        self.colors = 0  # tracks LR color palette index

        # canvas scrollbars
        self.xsb_frame = tk.Frame(self.frame)
        self.ysb_frame = tk.Frame(self.frame)

        self.xsb = tk.Scrollbar(
            self.xsb_frame, orient="horizontal", command=self.canvas.xview
        )
        self.ysb = tk.Scrollbar(
            self.ysb_frame, orient="vertical", command=self.canvas.yview
        )
        self.xsb.pack(fill="x", expand=True)
        self.ysb.pack(fill="y", expand=True)

        self.canvas.configure(
            xscrollcommand=self.xsb.set,
            yscrollcommand=self.ysb.set,
            scrollregion=(0, 0, 12000, 12000),
        )
        self.canvas.curr_coords = (0, 0)  # for statusbar tracking

        # keybinds for canvas mouse panning (linux)
        self.canvas.bind("<Alt-ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<Alt-B1-Motion>", self.scroll_move)

        # keybinds for canvas mouse panning (mac)
        self.canvas.bind("<Control-ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<Control-B1-Motion>", self.scroll_move)

        # bottom statusbar
        self.statusbar_frame = tk.Frame(self.frame)
        self.statusbar = tk.Label(
            self.statusbar_frame, text="Statusbar", bd=1, relief="sunken", anchor="w"
        )
        self.statusbar.pack(fill="both", expand=True)

        # statusbar elements
        self.day_indicator = ""
        self.override_indicator = ""
        self.inserting_indicator = ""

        # keybinds for statusbar updating
        self.canvas.bind("<Motion>", self.motion_track)
        self.canvas.bind("<KeyRelease>", self.motion_track)

        # highlighting/insertion tests
        self.highlight_choice = 0  # tracks highlighted root when cycling
        self.canvas.bind("<Right>", self.cycle_highlights)

        # place widgets using grid
        self.menu.grid(row=1, column=0, rowspan=3, sticky="news")
        self.title_frame.grid(row=0, column=1, columnspan=2, sticky="ew")
        self.canvas.grid(row=1, column=1, sticky="news")
        self.statusbar_frame.grid(row=3, column=1, columnspan=2, sticky="ew")
        self.xsb_frame.grid(row=2, column=1, sticky="ew")
        self.ysb_frame.grid(row=1, column=2, sticky="ns")

        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def ask_zoom_factor(self):
        """Prompt user to select a zoom factor after importing the first image."""

        def on_ok():
            try:
                # Retrieve the scale factor from the statusbar
                zoom = self.scale_factor
                print(
                    f"Zoom factor selected: {zoom}"
                )  # Debug print, remove if unnecessary
                self.zoom_factor = zoom  # Store zoom factor
                zoom_popup.destroy()
            except ValueError:
                print("Invalid input, zoom factor not updated.")

        def on_cancel():
            zoom_popup.destroy()

        zoom_popup = tk.Toplevel(self.base)
        zoom_popup.title("Choose Zoom")
        zoom_popup.geometry("200x150")

        label = tk.Label(zoom_popup, text="Choose the zoom factor")
        label.pack(pady=10)

        # OK and Cancel buttons
        ok_button = tk.Button(zoom_popup, text="OK", command=on_ok)
        ok_button.pack(side="left", padx=20)

        cancel_button = tk.Button(zoom_popup, text="Cancel", command=on_cancel)
        cancel_button.pack(side="right", padx=20)

    def click_info(self, event):
        """Show node metadata on right click (for debugging)."""
        for n in self.tree.nodes:  # check click proximity to existing points
            if ((abs(n.coords[0] - event.x)) < 10) and (
                (abs(n.coords[1] - event.y)) < 10
            ):
                self.canvas.create_text(
                    event.x,
                    event.y,
                    anchor="nw",
                    text=f"d{n.depth}/lri{n.LR_index}/deg{n.root_degree}",
                    fill="white",
                )

    def scroll_start(self, event):
        """Mouse panning start."""
        self.canvas.focus_set()  # allows canvas keybinds; put this in place_node() too
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        """Mouse panning track."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def motion_track(self, event):
        """Mouse position reporting for the statusbar."""
        if str(event.type) == "Motion":
            # convert mouse position to canvas position
            self.canvas.curr_coords = (
                int(self.canvas.canvasx(event.x)),
                int(self.canvas.canvasy(event.y)),
            )

        # update statusbar contents
        self.statusbar.config(
            text=f"{self.canvas.curr_coords}, {self.day_indicator}, {self.override_indicator}, {self.inserting_indicator}, {self.scale_factor}"
        )

    def import_image(self):
        """Query user for an input file and load it onto the canvas."""
        self.path = filedialog.askopenfilename(
            parent=self.base, initialdir="./", title="Select an image file:"
        )
        self.title_label.config(text=f"Tracing {self.path}")
        self.file = Image.open(self.path)

        # Default image without scaling for the first image
        if not self.first_image_imported:
            self.img = ImageTk.PhotoImage(self.file)
            self.ask_zoom_factor()  # Show zoom factor popup only for the first image
            self.first_image_imported = True
        else:
            scaled_image = self.file.resize(
                (
                    int(self.file.width * self.zoom_factor),
                    int(self.file.height * self.zoom_factor),
                ),
                Image.Resampling.LANCZOS,
            )
            self.img = ImageTk.PhotoImage(scaled_image)

        self.frame_id = self.canvas.create_image(0, 0, image=self.img, anchor="nw")

        # create gif iterator for pagination
        self.iterframes = ImageSequence.Iterator(self.file)
        self.frame_index = 0
        self.frame_id = self.canvas.create_image(0, 0, image=self.img, anchor="nw")

        # current tree
        self.tree = Tree(self.path)  # instantiate first tree

        self.history = deque(maxlen=6)  # gets updated on every add_node()

        # Enable buttons and add relevant keybinds
        self.canvas.bind("<Button 1>", self.place_node)

        self.button_save.config(command=self.make_file, state="normal")
        self.canvas.bind("g", self.make_file)

        self.button_next.config(command=self.next_day, state="normal")
        self.canvas.bind("e", self.next_day)

        self.button_prev.config(command=self.previous_day, state="normal")
        self.canvas.bind("q", self.previous_day)

        self.button_undo.config(command=self.undo, state="normal")
        self.canvas.bind("<Control-z>", self.undo)

        self.button_override.config(command=self.override, state="normal")
        self.canvas.bind("r", self.override)

        self.button_insert.config(command=self.insert, state="normal")
        self.canvas.bind("i", self.insert)

        self.button_show.config(command=self.show_tree, state="normal")
        self.canvas.bind("c", self.show_tree)

        self.button_change_root.config(command=self.change_root, state="normal")
        self.canvas.bind("c", self.change_root)

        self.button_zoom_in.config(command=self.zoom_in, state="normal")
        self.canvas.bind("+", self.zoom_in)

        self.button_zoom_out.config(command=self.zoom_out, state="normal")
        self.canvas.bind("-", self.zoom_out)

        # Prompt user to choose zoom factor after importing the first image
        # if not hasattr(self, 'zoom_factor'):
        # self.ask_zoom_factor()

    def change_frame(self, next_index):
        """Move frames in the GIF."""
        try:
            # get next frame from GIF
            new_frame = self.iterframes[next_index]

            # delete current canvas image
            self.canvas.delete(self.frame_id)

            # add the new image
            self.img = ImageTk.PhotoImage(new_frame)
            self.frame_id = self.canvas.create_image(0, 0, image=self.img, anchor="nw")

            # lower it into the background
            self.canvas.tag_lower(self.frame_id)

            # adjust index and menubar
            self.frame_index = next_index
            self.day_indicator = f"Frame #{self.frame_index+1}"

        except IndexError:
            self.day_indicator = "End of GIF"

    def next_day(self, event=None):
        """Show the next frame in the GIF."""
        self.change_frame(self.frame_index + 1)

    def previous_day(self, event=None):
        """Show the previous frame in the GIF."""
        self.change_frame(self.frame_index - 1)

    def place_node(self, event):
        """Place/select nodes on click."""
        ## TODO error handling: graph components (no parent)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.focus_set()

        # check click proximity to existing nodes
        if not self.prox_override:
            for n in self.tree.nodes:
                if ((abs(n.coords[0] - x)) < 10) and ((abs(n.coords[1] - y)) < 10):
                    if not n.is_selected:  # select a nearby unselected point
                        for m in self.tree.nodes:
                            m.deselect()
                        n.select()
                    self.color_nodes()
                    return

        # if inserting, check that root_choice exists (if needed)
        if self.inserting:
            for n in self.tree.nodes:
                if n.is_selected:
                    if len(n.children) > 1:
                        if self.tree.root_choice is None:
                            print(
                                "Please use the right arrow key to choose which root you'd like to insert on."
                            )
                            return

        # place a new point and select it
        idx = self.canvas.create_oval(
            x, y, x + 2, y + 2, width=2, fill="red", outline="red"
        )
        point = Node((x, y), idx, self.canvas, self.tree)

        hologram, draw = self.tree.add_node(point, self.inserting)
        self.history.append(
            hologram
        )  # save tree as it was just before new node was added

        self.tree.index_LRs()

        if self.inserting:
            self.redraw()  # update edges following add_node() above
            for n in self.tree.nodes:  # deselect all other points
                n.deselect()
            self.insert()  # turn off insertion mode after placing new point
        else:
            for n in self.tree.nodes:
                if n.is_selected:
                    self.draw_edge(n, point)
                n.deselect()

        if draw is not None:
            self.draw_edge(draw[0], draw[1])

        point.select()
        self.color_nodes()

        # turn off override mode after placing new point
        if self.prox_override:
            self.override()

        # reset insertion tracking
        self.tree.root_choice = None
        self.highlight_choice = 0

    def override(self, event=None):
        """Override proximity limit on node placement."""
        if self.prox_override:
            self.prox_override = False
            self.override_indicator = ""
            self.button_override.config(state="normal")
        else:
            self.prox_override = True
            self.override_indicator = "override=ON"
            self.button_override.config(state="active")

    def insert(self, event=None):
        """Insert a new middle node between 2 existing nodes."""
        if self.inserting:  # turn off insertion mode
            self.inserting = False
            self.inserting_indicator = ""
            self.button_insert.config(state="normal")
            if self.prox_override:  # turn off override too
                self.override()

            # remove any leftover highlights
            to_clear = set()
            for m in self.tree.nodes:
                if m.is_highlighted:
                    to_clear.add(m)
            self.highlight_nodes(to_clear)

        else:
            selected_count = 0
            for n in self.tree.nodes:
                if n.is_selected:
                    if len(n.children) == 0:
                        print("Warning: can't insert at terminal point")
                        return
                    else:
                        selected_count += 1
            if selected_count > 1:
                print("Warning: can't insert with >1 point selected")
                return

            # turn on insertion mode
            self.inserting = True
            self.inserting_indicator = "inserting=ON"
            self.button_insert.config(state="active")

            # turn on override too
            if not self.prox_override:
                self.override()

    def change_root(self, event=None):
        """Clear current tree, prompt for a new root, and reinitialize."""
        # Destroy all nodes and edges from the canvas
        for node in self.tree.nodes:
            self.canvas.delete(node.shape_val)
        for edge in self.tree.edges:
            self.canvas.delete(edge)

        # Clear the current tree data
        self.tree.clear_tree()

        # Reset necessary states
        self.history.clear()
        self.tree.root_choice = None
        self.highlight_choice = 0
        self.day_indicator = ""

        # Prompt for a new plant ID assignment and create a new tree
        self.tree.popup(self.base)

    # Zoom function
    # zoom in
    def zoom_in(self):
        self.scale_factor *= 1.5  # Increase scale
        self.update_image()
        self.update_statusbar()  # Update the status bar with zoom info

    # Zoom out
    def zoom_out(self):
        self.scale_factor /= 1.5  # Decrease scale
        self.update_image()
        self.update_statusbar()  # Update the status bar with zoom info

    def update_image(self):
        """Update the image on the canvas based on the scale factor."""
        if self.img and self.file:
            # Resize the image based on the scale factor
            scaled_image = self.file.resize(
                (
                    int(self.file.width * self.scale_factor),
                    int(self.file.height * self.scale_factor),
                ),
                Image.Resampling.LANCZOS,  # Use LANCZOS for high-quality downscaling
            )
            self.img = ImageTk.PhotoImage(scaled_image)

            # Update the canvas with the new image
            self.canvas.itemconfig(self.frame_id, image=self.img)

            # Update the scroll region to match the new image size
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Update the status bar with the current zoom level
        self.update_statusbar()

    def update_statusbar(self):
        """Update the status bar text with scale factor and other information."""
        self.statusbar.config(
            text=f"{self.canvas.curr_coords}, {self.day_indicator}, "
            f"{self.override_indicator}, {self.inserting_indicator}, "
            f"Zoom Scale: {self.scale_factor}"
        )

    def draw_edge(self, parent_node, child_node):
        """Draw an edge between 2 nodes, and add it to the tree."""
        # TODO: test that checks if drawn edge matches the data/hierarchy
        if child_node.root_degree == 0:  # PR
            color = "green"
        elif parent_node.root_degree < child_node.root_degree:  # branch point
            if child_node.pedge_color is None:  # nascent LR
                color = self.get_color()
            else:  # existing LR, already indexed (insertion mode)
                color = child_node.pedge_color
        else:  # LR
            color = parent_node.pedge_color

        edge = self.canvas.create_line(
            parent_node.coords[0],
            parent_node.coords[1],
            child_node.coords[0],
            child_node.coords[1],
            fill=color,
            state=f"{self.tree_flag}",
        )
        self.tree.edges.append(edge)
        child_node.pedge = edge
        child_node.pedge_color = color

    def get_color(self):
        """Fetch a new LR color from the palette."""
        palette = [
            # seaborn colorblind
            "#0173B2",  # dark blue
            "#DE8F05",  # orange
            "#029E73",  # green
            "#D55E00",  # red orange
            "#CC78BC",  # violet
            "#CA9161",  # tan
            "#FBAFE4",  # pink
            "#ECE133",  # yellow
            "#56B4E9",  # light blue
        ]
        # 'green', # PR
        # 'red', # selected node
        # 'white', # unselected node

        pos = (self.colors - len(palette)) % len(palette)
        self.colors += 1
        return palette[pos]  # next color

    def undo(self, event=None):
        """Undo the last graph-altering action."""
        ## comment this better
        try:
            previous = self.history.pop()
            for n in self.tree.nodes:
                self.canvas.delete(n.shape_val)
            for e in self.tree.edges:
                self.canvas.delete(e)
            self.tree.edges = []

            self.tree = previous

            for n in self.tree.nodes:
                x = n.coords[0]
                y = n.coords[1]
                if not n.is_selected:
                    n.shape_val = self.canvas.create_oval(
                        x, y, x + 2, y + 2, width=1, fill="white", outline="white"
                    )
                else:
                    n.shape_val = self.canvas.create_oval(
                        x, y, x + 2, y + 2, width=2, fill="red", outline="red"
                    )

            self.redraw()

        except IndexError as e:  # end of history deque
            print(e)
            pass

    def redraw(self):
        """Redraw the current tree's edges."""
        # 1) delete existing tree's edges
        for e in self.tree.edges:
            self.canvas.delete(e)
        self.tree.edges = []

        # 2) redraw it based on new nodes
        for n in self.tree.nodes:
            for m in n.children:
                x = self.canvas.create_line(
                    m.coords[0],
                    m.coords[1],
                    n.coords[0],
                    n.coords[1],
                    fill=m.pedge_color,
                    state=f"{self.tree_flag}",
                )
                self.tree.edges.append(x)

    def show_tree(self, event=None):
        """Toggle visibility of tree edges."""
        if self.tree.is_shown is False:
            self.tree_flag = "normal"
            self.tree.is_shown = True
        else:
            self.tree_flag = "hidden"
            self.tree.is_shown = False

        for e in self.tree.edges:
            self.canvas.itemconfig(e, state=f"{self.tree_flag}")

    def color_nodes(self):
        """Refresh node colors to reflect whether they are selected/deselected."""
        for n in self.tree.nodes:
            if n.is_selected:
                self.canvas.itemconfig(n.shape_val, fill="red", outline="red", width=2)
            else:
                self.canvas.itemconfig(
                    n.shape_val, fill="white", outline="white", width=1
                )

    def find_root(self, n, excluded):
        """Return all the nodes on the root that a node (n) belongs to, except any excluded nodes."""
        # TODO: can probably
        targets = set()

        if len(n.children) > 1:  # n is a branch point, so it belongs to multiple roots
            targets.add(n)  # only highlight it
        else:
            if n.root_degree == 0:  # PR
                for m in self.tree.nodes:
                    if m.root_degree == 0:
                        targets.add(m)
            else:  # LR
                for m in self.tree.nodes:
                    if m.LR_index == n.LR_index:
                        targets.add(m)

        targets.discard(excluded)

        return targets

    def highlight_nodes(self, targets):
        """Highlight/unhighlight a set of nodes."""
        for i in targets:
            if not i.is_highlighted:
                self.canvas.itemconfig(
                    i.shape_val, fill="yellow", outline="yellow", width="2"
                )
                i.is_highlighted = True
            else:  # un-highlight
                self.canvas.itemconfig(
                    i.shape_val, fill="white", outline="white", width="1"
                )
                i.is_highlighted = False

    def cycle_highlights(self, event=None):
        """Cycle thru children of a branch point (for insertion mode)."""
        if self.inserting:
            for n in self.tree.nodes:
                if n.is_selected:
                    # first, clear all current highlights
                    to_clear = set()
                    for m in self.tree.nodes:
                        if m.is_highlighted:
                            to_clear.add(m)
                    self.highlight_nodes(to_clear)

                    # now, highlight the current highlight_choice
                    pos = (self.highlight_choice - len(n.children)) % len(n.children)
                    self.tree.root_choice = n.children[pos]  # save the current choice

                    to_show = set()
                    to_show.add(self.tree.root_choice)
                    self.highlight_nodes(to_show)

                    # get ready for next call
                    self.highlight_choice += 1
        else:
            self.base.bell()

    def EG_highlight_root(self, event=None):
        # if the node belongs to >1 root, skip
        for point in self.tree.nodes:
            if point.is_selected:
                n = point

        if len(n.children) > 1:
            return
        else:
            targets = []

            if n.root_degree == 0:  # highlight PR
                for m in self.tree.nodes:
                    if m.root_degree == 0:
                        targets.append(m)
            else:  # highlight an LR
                # self.tree.index_LRs() ## i don't think we need this here
                for m in self.tree.nodes:
                    if m.LR_index == n.LR_index:
                        targets.append(m)

            for i in targets:
                self.canvas.itemconfig(
                    i.shape_val, fill="green", outline="green", width="2"
                )

    def make_file(self, event=None):
        """Output tree data to file."""
        if self.tree.plant is None:  # get plant ID when called for the first time
            self.tree.popup(self.base)
            if self.tree.plant is None:  # user didn't update ID (pressed cancel)
                return

        self.tree.index_LRs()

        # prepare output file
        source = Path(self.tree.path.replace(" ", "")).stem  # input name, no spaces
        output_name = f"{source}_plant{self.tree.plant}_day{self.frame_index + 1}.json"
        repo_path = Path("./").resolve()
        output_path = repo_path / output_name

        # convert Tree to NX graph
        DG = nx.DiGraph()

        # make ebunches (2-tuples of adjacent nodes)
        ebunches = []
        for node in self.tree.nodes:
            # add nodes w/ positions and LR indices
            DG.add_node(
                node.relcoords,
                pos=node.relcoords,
                LR_index=node.LR_index,
                root_deg=node.root_degree,
            )

            for child in node.children:
                ebunches.append((node.relcoords, child.relcoords))

        DG.add_edges_from(ebunches)
        DG = nx.convert_node_labels_to_integers(DG)

        s = json_graph.adjacency_data(DG)

        with open(output_path, mode="w") as h:
            json.dump(s, h)
            print(f"wrote to output {output_name}")


class Node:
    """An (x,y,0) point along a root."""

    def __init__(self, coords, shape_val, canvas, tree):
        self.coords = coords  # (x,y) tuple
        self.relcoords = None  # (x,y) relative to root node
        self.shape_val = shape_val  # canvas object ID
        self.is_selected = False
        self.is_visited = False  # for DFS; remember to clear it!
        self.depth = None  # depth of node in the tree, relative to root
        self.children = []
        self.LR_index = None  # each distinct LR has a unique index
        self.root_degree = (
            None  # 0 = PR, 1 = primary LR, 2 = secondary LR, None = not yet determined
        )
        self.is_highlighted = False

        self.pedge = None  # id of parent_node edge incident upon node
        self.pedge_color = None

    def select(self):
        self.is_selected = True

    def deselect(self):
        self.is_selected = False


class Tree:
    """An acyclic, undirected, connected, hierarchical collection of nodes."""

    def __init__(self, path):
        self.nodes = []
        self.edges = []
        self.plant = None  # ID of plant on plate (e.g. A-E, from left to right)
        self.is_shown = True  # toggle display of edges
        self.top = None  # keep track of root node at top of tree
        self.path = path  # path to image source file where tree is being made
        self.num_LRs = 0  # use for indexing
        self.root_choice = None  # which node to use as child when inserting

    def add_node(self, obj, inserting):
        """Add a node to the tree."""
        hologram = copy.deepcopy(self)  # save tree each time a node is to be added

        if self.nodes:  # non-empty
            for n in self.nodes:
                if n.is_selected:
                    obj.depth = n.depth + 1  # child is one level lower
                    obj.relcoords = (
                        (obj.coords[0] - (self.nodes[0].coords[0])),
                        (obj.coords[1] - (self.nodes[0].coords[1])),
                    )

                    if inserting is True:
                        self.insert_child(n, obj)
                        draw = (
                            n,
                            obj,
                        )  # call draw_edge once back at the UI level in place_node()
                    else:
                        self.add_child(n, obj)
                        draw = None

        else:  # if no nodes yet assigned
            obj.depth = 0
            obj.relcoords = (0, 0)
            self.top = obj
            obj.root_degree = 0
            draw = None

        # finally, add to tree (avoid self-assignment)
        self.nodes.append(obj)

        return hologram, draw

    def clear_tree(self):
        """Clear all nodes and edges from the tree."""
        self.nodes = []
        self.edges = []
        self.top = None
        self.num_LRs = 0
        self.root_choice = None

    def popup(self, base):
        """Popup menu for plant ID assignment."""
        top = tk.Toplevel(base)
        top.geometry("350x200")

        label = tk.Label(top, text="Please enter a plant ID:")
        label.pack(side="top", fill="both", expand=True)

        v = tk.StringVar()  # holds plant ID

        # Entry widget for typing the ID
        entry = tk.Entry(top, textvariable=v, font=("Arial", 14))
        entry.pack(pady=20)
        entry.focus_set()  # focus on the entry for convenience

        def updater():
            top.destroy()
            self.plant = v.get()

        ok = tk.Button(top, text="OK", command=updater)
        cancel = tk.Button(top, text="Cancel", command=top.destroy)

        ok.pack(side="left", padx=20, pady=10, expand=True)
        cancel.pack(side="right", padx=20, pady=10, expand=True)

        base.wait_window(top)  # wait for a button to be pressed

    ##########################
    def insert_child(self, current_node, new):
        """Assign child when using insertion mode."""
        if len(current_node.children) == 1:  # easy case
            new.children.append(current_node.children[0])
            del current_node.children[0]
            current_node.children.append(new)

            # if current_node.root_degree == 0:
            #     new.root_degree = 0
            new.root_degree = current_node.root_degree
            new.LR_index = current_node.LR_index
            new.pedge_color = current_node.pedge_color

        else:  # use root_choice
            new.children.append(self.root_choice)
            current_node.children.remove(self.root_choice)
            current_node.children.append(new)

            new.root_degree = self.root_choice.root_degree
            new.LR_index = self.root_choice.LR_index
            new.pedge_color = self.root_choice.pedge_color

        new.children[0].depth += 1
        self.DFS(new.children[0])

    ##########################

    def add_child(self, current_node, new):
        """Assign child in all other cases."""
        if len(current_node.children) == 0:
            if current_node.root_degree == 0:
                new.root_degree = 0

        current_node.children.append(new)

    def DFS(self, root):
        """Walk tree depth-first and increment subtree depths +1. For insertion mode."""
        root.is_visited = True
        for child in root.children:
            if child is not None and child.is_visited is False:
                child.depth += 1
                child.is_visited = True
                self.DFS(child)

        # reset is_visited flags when done!
        for node in self.nodes:
            node.is_visited = False

    def index_LRs(self):
        """Walk tree breadth-first and assign indices to lateral roots."""
        q = Queue()
        q.put(self.top)

        while not q.empty():
            current_node = q.get()
            # arbitrarily, we assign LR indices left-to-right
            # sort by x-coordinate
            current_node_children = sorted(
                current_node.children, key=lambda x: x.relcoords[0]
            )

            for n in current_node_children:
                if n.root_degree is None:  # only index nodes that haven't been already
                    if (
                        len(current_node_children) == 1
                    ):  # then n is part of the same root as current_node
                        n.root_degree = current_node.root_degree
                        if current_node.LR_index is not None:
                            n.LR_index = current_node.LR_index
                    else:  # current_node is a branch point (aka LR found)
                        n.root_degree = current_node.root_degree + 1
                        n.LR_index = self.num_LRs
                        self.num_LRs += 1
                q.put(n)


class AnalyzerUI(tk.Frame):
    """Analysis mode interface."""

    def __init__(self, base):
        super().__init__(base)
        self.base = base
        self.base.geometry("750x600")
        self.base.title("Ariadne: Analyze")

        # Initialize scale factors with defaults first
        self.length_scale_factor = 1.0
        self.length_scale_unit = "px"

        # master frame
        self.frame = tk.Frame(self.base)
        self.frame.pack(side="top", fill="both", expand=True)

        # left-hand menu
        self.left_frame = tk.Frame(self.frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.load_button = tk.Button(
            self.left_frame, text="Load file(s)", command=self.import_file
        )
        self.load_button.pack(side="top", expand=True)

        # right-hand output
        self.right_frame = tk.Frame(self.frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.output_info = "Current files:"
        self.output = tk.Label(self.right_frame, text=self.output_info)
        self.output.pack(side="top", fill="both", expand=True)

        # Ask user for scale info at startup
        self.ask_scale()

    def ask_scale(self):
        """Pop up window to set scale before analysis."""
        # Create custom popup window
        scale_win = tk.Toplevel(self.base)
        scale_win.title("Set Scale")
        scale_win.geometry("350x350")
        scale_win.grab_set()  # make popup modal

        # Labels + Entries
        tk.Label(scale_win, text="1) Distance in pixels:").pack(pady=5)
        pixels_entry = tk.Entry(scale_win)
        pixels_entry.pack(pady=5)

        tk.Label(scale_win, text="2) Distance in (real units):").pack(pady=5)
        real_entry = tk.Entry(scale_win)
        real_entry.pack(pady=5)

        tk.Label(scale_win, text="3) Unit of length (e.g., mm, cm):").pack(pady=5)
        unit_entry = tk.Entry(scale_win)
        unit_entry.pack(pady=5)

        # Label to show calculated scale
        result_label = tk.Label(scale_win, text="Result: (waiting for input...)")
        result_label.pack(pady=10)

        def update_result(*args):
            """Update live result when values change."""
            try:
                pixels = float(pixels_entry.get())
                real_dist = float(real_entry.get())
                if pixels > 0 and real_dist > 0:
                    scale = real_dist / pixels
                    result_label.config(
                        text=f"Result: 1 pixel = {scale:.4f} {unit_entry.get().strip()}"
                    )
                else:
                    result_label.config(text="Result: invalid numbers")
            except ValueError:
                result_label.config(text="Result: waiting for valid input...")

        # Bind events so that division updates live
        pixels_entry.bind("<KeyRelease>", update_result)
        real_entry.bind("<KeyRelease>", update_result)
        unit_entry.bind("<KeyRelease>", update_result)

        def submit_scale():
            try:
                pixels = float(pixels_entry.get())
                real_dist = float(real_entry.get())
                unit = unit_entry.get().strip()

                if pixels <= 0 or real_dist <= 0 or unit == "":
                    raise ValueError("Invalid values provided.")

                # Store scale factors as instance variables (for immediate use)
                self.length_scale_factor = real_dist / pixels
                self.length_scale_unit = unit

                # Store in config module for analysis workflow
                config.length_scale_factor = self.length_scale_factor
                config.length_scale_unit = self.length_scale_unit

                messagebox.showinfo(
                    "Scale set",
                    f"1 pixel = {self.length_scale_factor:.4f} {self.length_scale_unit}",
                )
                scale_win.destroy()

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Please enter valid numeric values for distances and a unit.",
                )

        submit_btn = tk.Button(scale_win, text="OK", command=submit_scale)
        submit_btn.pack(pady=10)

        # Center popup and block main window until closed
        self.base.wait_window(scale_win)

    def import_file(self):
        """Load input files."""
        self.tree_paths = filedialog.askopenfilenames(
            parent=self.base, initialdir="./", title="Select files to analyze:"
        )

        if len(self.tree_paths) == 0:  # no selection made
            return

        # Inform user about next step
        messagebox.showinfo(
            "Select Output Folder",
            f"Selected {len(self.tree_paths)} file(s) for analysis.\n\n"
            "Next: Choose where to save the results (CSV report and plots).",
        )

        # Get output folder
        output_folder = filedialog.askdirectory(
            parent=self.base,
            initialdir="./",
            title="Select output folder for analysis results (CSV & plots):",
            mustexist=True,
        )

        # Check if user cancelled
        if not output_folder:
            messagebox.showwarning(
                "Cancelled", "No output folder selected. Analysis cancelled."
            )
            return

        self.output_path = Path(output_folder)

        # create a csv to store analysis results
        timestamp = datetime.now()
        report_dest = (
            self.output_path / f"report_{str(timestamp.strftime('%Y%m%d_%H%M%S'))}.csv"
        )

        # add current file count
        self.output_info = f"Current files: ({len(self.tree_paths)})"
        i = 1

        for json_file in self.tree_paths:
            graph_name = json_file.split("/")[-1]
            graph_name_noext = graph_name[:-5]
            pareto_name = graph_name_noext + "_pareto.png"
            # plot_name = graph_name_noext + '_tree.png'
            pareto_path = self.output_path / pareto_name

            # update current file count list
            self.output_info = self.output_info + "\n" + graph_name
            self.output.config(text=self.output_info)

            # load and process graph data
            with open(json_file, mode="r") as h:
                data = json.load(h)

                # Validate JSON format - must be networkx adjacency format
                if (
                    not isinstance(data, dict)
                    or "nodes" not in data
                    or "adjacency" not in data
                ):
                    error_msg = (
                        f"Invalid JSON format in {graph_name}\n\n"
                        "Expected networkx adjacency format with 'nodes' and 'adjacency' keys.\n"
                        "This file appears to be in a different format (possibly a tree/node format).\n\n"
                        "Only JSON files exported from the Ariadne tracer can be analyzed.\n"
                        "Test fixture files (test_*.json) are for unit testing only."
                    )
                    messagebox.showerror("Invalid File Format", error_msg)
                    return

                graph = json_graph.adjacency_graph(data)

                # perform analysis
                results, front, randoms = quantify.analyze(graph)
                results["filename"] = graph_name_noext

                # Apply scaling transformation to results
                scaled_results = scaling.apply_scaling_transformation(
                    results, self.length_scale_factor
                )

                # Write scaled results to CSV
                with open(report_dest, "a", encoding="utf-8", newline="") as csvfile:
                    w = csv.DictWriter(csvfile, fieldnames=scaled_results.keys())
                    if i == 1:  # Write header only for the first file
                        w.writeheader()
                    w.writerow(scaled_results)

                # debug
                logging.debug(f"Total root length: {results['Total root length']}")
                logging.debug(f"Travel distance: {results['Travel distance']}")
                logging.debug(
                    f"Total root length (random): {results['Total root length (random)']}"
                )
                logging.debug(
                    f"Travel distance (random): {results['Travel distance (random)']}"
                )

                # make pareto plot and save
                quantify.plot_all(
                    front,
                    [results["Total root length"], results["Travel distance"]],
                    randoms,
                    results["Total root length (random)"],
                    results["Travel distance (random)"],
                    pareto_path,
                )

                print(f"Processed file {i}/{len(self.tree_paths)}")
                i += 1

        # show confirmation message
        print("Finished.")

        # Show completion dialog with output locations
        completion_msg = (
            f"Analysis Complete!\n\n"
            f"Processed {len(self.tree_paths)} file(s)\n\n"
            f"Output folder: {self.output_path}\n\n"
            f"Generated files:\n"
            f"  • CSV report: {report_dest.name}\n"
            f"  • Pareto plots: {len(self.tree_paths)} PNG file(s)\n\n"
            f"You can now open the output folder to view results."
        )
        messagebox.showinfo("Analysis Complete", completion_msg)

    def clear(self):
        """Clean up a previously imported file."""
        # take care of self.path, self.results, buttons, etc
        pass


def main():
    base = tk.Tk()
    base.title("Ariadne")
    StartupUI(base)
    base.mainloop()


if __name__ == "__main__":
    main()
