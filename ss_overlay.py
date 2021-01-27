"""This script contains functions for generating and handling stride secondary structure assignments
and a class for adding secondary structure overlays to matplotlib plots where residue numbers are on the x axis.

There is much room for improvement but this should already generalise well.

The secondary_structure_overlay class generates the secondary structure overlay on the axis when you create an object of
    this class.

The generate_stride_ss_file function will use the stride program (http://webclu.bio.wzw.tum.de/stride/) to generate a
    stride assignment file from an input pdb. Stride must be available and executable.

The secondary_structure_assignment function reads a given stride file and resturns a list of lists
    providing a list of all secondary structure segments, their structure class and residue start and end points.

To use, import this script into your main program, or copy the class/functions as required.
    See example_generation_of_histogram.py script for an example implementation.

- Kyle (27/01/21)
"""

from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from copy import deepcopy
import os

class secondary_structure_overlay:
    """
    Given a matplotlib ax object, a list of residue numbers, and a list of secondary structure class labels
         this class will generate a secondary structure overlay on the axis.
    """
    def __init__(self,ax,residue_numbers,ss_segment_list):
        """ This method is called upon creation of secondary_structure_overlay_object.
        :param ax: matplotlib ax object
        :param residue_numbers: list of residue numbers
        :param secondary_structure_class_list: list of lists.
        Each element in the top level list is a nested list containing info for a single continuous secondary structure segment.
        Each element in the nested lists is a string.
        The nested lists have format ['SSclass','First res 3 letter AA code','First res num','Last res 3 letter AA code','Last res num']
        For example:
         secondary_structure_class_list = [['AlphaHelix', 'GLU', '79', 'MET', '99'], ['Strand', 'GLU', '4', 'LYS', '12']]
        """
        # initialise class variables
        self.ax = ax
        self.residue_numbers = residue_numbers
        self.ss_segment_list = ss_segment_list

        # generate the secondary structure overlay
        print("Initiated secondary_structure_overlay object, generating overlay now...")
        self.find_ss_segments_and_generate_overlay()
        print("Generated overlay.")
        print("-------------------------------------------------------------")

    def find_ss_segments_and_generate_overlay(self):
        # find and plot secondary structure patches
        # NOTE: only strands and helices are recognised currently, everything else is considered 'unstructured'.
        # We will
        # 1. make a copy of the residue number list called residues_without_ss_assignment.
        # 2. loop over self.ss_segment_list and when a strand or helix is found we will call the appropriate method for
        #   generating the patch on ax and remove these residues from residues_without_ss_assignment.
        # 3. Once all structured segments are plotted we will loop over the remaining elements in
        #   residues_without_ss_assignment to plot a straight line corresponding to unstructured residues.
        residues_without_ss_assignment = deepcopy(self.residue_numbers)
        for x in range(0,len(self.ss_segment_list)):
            # step 2. as described above
            if self.ss_segment_list[x][0] == 'Strand':
                # add strand patch
                self.add_strand_patch(self.ss_segment_list[x][2],self.ss_segment_list[x][4])
                for y in range(self.ss_segment_list[x][2],self.ss_segment_list[x][4]):
                    # remove these residues from structureless list
                    residues_without_ss_assignment.remove(y)
            elif self.ss_segment_list[x][0] == 'AlphaHelix':
                # add helix patch
                self.add_helix_patch(self.ss_segment_list[x][2],self.ss_segment_list[x][4])
                for y in range(self.ss_segment_list[x][2],self.ss_segment_list[x][4]):
                    # remove these residues from structureless list
                    residues_without_ss_assignment.remove(y)
        for x in range(0,len(residues_without_ss_assignment)):
            # step 3. as described above, adding thin rectangles for unassigned residues
            if int(residues_without_ss_assignment[x]) == self.residue_numbers[0]:
                # special case if 1st residue is unassigned
                self.add_rectangle_patch(int(residues_without_ss_assignment[x])+1, 1)
            else:
                # for all other unassigned residues
                self.add_rectangle_patch(int(residues_without_ss_assignment[x]),1)

    def add_strand_patch(self,strand_start,strand_end):
        # add patch to ax for a strand (uses mpatches FancyArrow)
        x_lims = plt.xlim()
        y_lims = plt.ylim()
        arrow_head_width = 0.1
        arrow_head_length = 1.5
        strand = mpatches.FancyArrow(strand_start-1, y_lims[1] + 0.08, strand_end - strand_start, 0, clip_on=False, head_length=arrow_head_length,
                                     head_width=arrow_head_width, width=arrow_head_width / 2.5, length_includes_head=True,edgecolor='k',facecolor='w')
        self.ax.add_patch(strand)
        self.add_rectangle_patch(strand_end,1)

    def add_helix_patch(self,helix_start,helix_end):
        # add patch for figure for (uses several overlapping mpatches Arc objects)
        x_lims = plt.xlim()
        y_lims = plt.ylim()
        no_turns = 1
        height = 0.1
        length = 0.75
        st_theta, en_theta = 0, 180
        for t_start in np.arange(helix_start-1, helix_end-1, length):  # turns
            origin = (t_start + 0.25, y_lims[1]+0.08)
            e = mpatches.Arc(origin, length, height,
                                linewidth=0.75,
                                # Add a bit to each angle to avoid sharp cuts
                                # that show as white lines in plot
                                theta1=st_theta - 1, theta2=en_theta + 1,clip_on=False)
            st_theta += 180
            en_theta += 180
            self.ax.add_patch(e)
        if helix_end < int(self.residue_numbers[-1]):
            # if not c-terminus then also add a connector
            self.add_rectangle_patch(helix_end, 1)

    def add_rectangle_patch(self,start,length):
        # add thin rectangular patch (to create a line for unstructured regions)
        x_lims = plt.xlim()
        y_lims = plt.ylim()
        rectangle = mpatches.Rectangle((start-1,y_lims[1]+0.08),length,0.0001,linewidth=1,edgecolor='k',facecolor='None',clip_on=False)
        self.ax.add_patch(rectangle)

def generate_stride_ss_file(input_structure_file,output_stride_file,path_to_stride_binary="stride"):
    """
    Runs stride to generate secondary structure assignment file. See http://webclu.bio.wzw.tum.de/stride/ for stride.
    :param input_structure_file: [str] input pdb file path/name
    :param output_stride_file: [str] output file path/name
    :param path_to_stride_binary: [str] location of stride binary. By default assumes stride is in current folder,
    but can be specified upon call. Note stride binary must be executable.
    :return: generates file but does not explicitly return (implicitly returns None)
    """
    os.system("./%s %s > %s" % (path_to_stride_binary,input_structure_file, output_stride_file))

def read_secondary_structure_assignment(path_to_stride_file):
    """
    Takes stride file and returns secondary structure assignment.
    :param path_to_stride_file: [str] path to stride file, if in current folder can set this to file name
    :return: secondary_structure_summary, which is a list of lists.
        Each element in the top level list is a nested list containing info for a single continuous secondary structure segment.
        Each element in the nested lists is a string.
        The nested lists have format ['SSclass','First res 3 letter AA code','First res num','Last res 3 letter AA code','Last res num']
        For example:
         secondary_structure_class_list = [['AlphaHelix', 'GLU', '79', 'MET', '99'], ['Strand', 'GLU', '4', 'LYS', '12']]
    """
    stride_lines = open(path_to_stride_file).read().splitlines()
    LOC_lines = []
    for x in range(0,len(stride_lines)):
        if stride_lines[x][:3] == 'LOC':
            LOC_lines.append(stride_lines[x])
    print("Obtaining secondary structure segments from stride file. Secondary structure segments:")
    for x in range(0,len(LOC_lines)):
        LOC_lines[x] = LOC_lines[x].replace("-","").replace("LOC","").replace("~","").replace(" A ","").replace(" B ","").split(" ")
        while "" in LOC_lines[x]:
            LOC_lines[x].remove("")
        LOC_lines[x][2] = int(LOC_lines[x][2])
        LOC_lines[x][4] = int(LOC_lines[x][4])
        print(LOC_lines[x])
    secondary_structure_summary = LOC_lines
    print("Completed secondary structure assignment and interpretation")
    print("-------------------------------------------------------------")
    return(secondary_structure_summary)