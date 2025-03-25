'''
Author: Shuoyu Chen shuoyuchen.physics@gmail.com
Date: 2025-03-03 16:17:54
LastEditors: Shuoyu Chen shuoyuchen.physics@gmail.com
LastEditTime: 2025-03-04 14:37:35
FilePath: /schen/workspace/HKFDML/tool/HKdisplay.py
Description: 
'''
import math
from root_file_utils import *
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import os
import mpld3
from mpld3 import plugins
import matplotlib.font_manager as fm
font_path = os.path.expanduser('/disk03/usr8/schen/font/times-new-roman.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    title_font = fm.FontProperties(fname=font_path, size=16, weight='bold')
    info_font = fm.FontProperties(fname=font_path, size=8, weight='bold')
    zaxi_font = fm.FontProperties(fname=font_path, size=12, weight='bold')

ROOT.gROOT.SetBatch(True)

def get_args():
    parser = argparse.ArgumentParser(description='Display PMT geometry from WCSim root file')
    parser.add_argument('input', type=str, help='Input ROOT file')
    parser.add_argument('-e', '--event', type=int, default=0, help='Event index to display')
    parser.add_argument('-t', '--time', action='store_true', help='Display time instead of charge')
    parser.add_argument('-o', '--output', type=str, default='plot.png', help='Output file name')
    args = parser.parse_args()
    return args

def cal_angle(a, b):
    dot = a[0] * b[0] + a[1] * b[1]
    aval = math.sqrt(a[0]**2 + a[1]**2)
    bval = math.sqrt(b[0]**2 + b[1]**2)
    if aval == 0 or bval == 0:
        raise ValueError("Length of a or b is zero.")
    cos_angle = dot / (aval * bval)
    cos_angle = max(min(cos_angle, 1.0), -1.0)
    angle = math.acos(cos_angle)
    return angle

def plot_geo(input_file):
    print("Input file:", input_file)
    file = WCSimFile(input_file)
    geo = file.geo
    num_pmts = geo.GetWCNumPMT()

    pmt_image_positions = np.zeros((num_pmts, 2))
    radius = 0
    height = 0
    print("num_pmts:", num_pmts)
    
    for i in range(num_pmts):
        tube = geo.GetPMTPtr(i)
        if tube.GetCylLoc() == 1:
            radius = math.sqrt(tube.GetPosition(0)**2 + tube.GetPosition(1)**2)
            break

    for i in range(num_pmts):
        tube = geo.GetPMTPtr(i)
        if tube.GetCylLoc() == 0:
            height = 2 * tube.GetPosition(2)
            break
    
    print("radius:", radius)
    print("height:", height/2)
    for i in range(num_pmts):
        pmt = geo.GetPMT(i)
        if pmt.GetCylLoc() == 0:
            pmt_image_positions[i][0] = pmt.GetPosition(1)
            pmt_image_positions[i][1] = pmt.GetPosition(0) + radius + height/2  +1 -39.854
        elif  pmt.GetCylLoc() == 2:
            pmt_image_positions[i][0] = pmt.GetPosition(1)
            pmt_image_positions[i][1] = -(pmt.GetPosition(0) + radius + height/2 +1)  - 27.974
        else:
            zero = [-1, 0]
            values = [pmt.GetPosition(0), pmt.GetPosition(1)]
            angle = cal_angle(zero, values)
            length = angle * radius
            if pmt.GetPosition(1) < 0:
                length *= -1

            pmt_image_positions[i][0] = length
            pmt_image_positions[i][1] = pmt.GetPosition(2) 


    for i in range(num_pmts):
        pmt_image_positions[i][0] = round((pmt_image_positions[i][0] +10152.68) / 35.35)
        pmt_image_positions[i][1] = round((pmt_image_positions[i][1] + 9717.43 + 27.974 ) / 35.32)
    
    positions_dict = {i: (pmt_image_positions[i][0], pmt_image_positions[i][1]) for i in range(num_pmts)}
    return positions_dict

def plot_charge( event_index, input_file, positions_dict, output_file):
    wcsim = WCSimFile(input_file)
    nevents = wcsim.nevent
    print(nevents,"events in file.")
    print("Now, we display event", event_index)

    wcsim.get_event(event_index)
    event_info = wcsim.get_event_info()
    pid = event_info["pid"]
    if pid == 11:
        particle_str = "Electron"
    elif pid == 13:
        particle_str = "Muon"
    elif pid == 22:
        particle_str = "Gamma"
    else:
        particle_str = "Unknown"

    position = event_info["position"]
    direction = event_info["direction"]
    energy = event_info["energy"]
    geo = wcsim.geo
    num_pmts = geo.GetWCNumPMT()
    digi_hits = wcsim.get_digitized_hits()
    digi_hit_pmt = digi_hits["pmt"]
    digi_hit_charge = digi_hits["charge"]
    print("File name:",os.path.basename(input_file))
    print("Index of the event:", event_index)
    print("Number of triggers:", wcsim.ntrigger)
    print("Particle:", particle_str)
    print("Energy: {:.1f} MeV".format(energy))
    print("Position: ({:.1f}, {:.1f}, {:.1f}) cm".format(position[0], position[1], position[2]))
    print("Direction: ({:.2f}, {:.2f}, {:.2f})".format(direction[0], direction[1], direction[2]))

    charges = np.zeros(num_pmts)
    for pmt, ch in zip(digi_hit_pmt, digi_hit_charge):
        if pmt < num_pmts:
            charges[pmt] += ch

    sorted_indices = sorted(positions_dict.keys())
    positions_array = np.array([positions_dict[i] for i in sorted_indices])
    charges_ordered = np.array([charges[i] for i in sorted_indices])
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(positions_array[:, 0], positions_array[:, 1], s=1, c=charges_ordered, cmap='viridis', marker='o')
    ax.set_title("Hyper-K Event Display".format(event_index),fontproperties=title_font)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = plt.colorbar(sc, ax=ax, label="charge")
    cb.ax.yaxis.label.set_fontproperties(zaxi_font)
    info_text = (
    "Index of the event: {}\n"
    "Number of triggers: {}\n"
    "Particle: {}\n"
    "Energy: {:.1f} MeV\n"
    "Direction: ({:.2f}, {:.2f}, {:.2f})\n"
    "Position: ({:.1f}, {:.1f}, {:.1f}) cm"
).format( event_index, wcsim.ntrigger, particle_str, energy,
          direction[0], direction[1], direction[2],position[0], position[1], position[2])

    fig.text(0.53, 0.85, info_text, ha='left', va='top', fontproperties=info_font)

    fig.savefig(output_file)
    print("Static image saved as", output_file)

    return positions_dict







def plot_time( event_index, input_file, positions_dict,output_file):
    wcsim = WCSimFile(input_file)
    nevents = wcsim.nevent
    print(nevents,"events in file.")
    print("Now, we display event", event_index)

    wcsim.get_event(event_index)
    event_info = wcsim.get_event_info()
    pid = event_info["pid"]
    if pid == 11:
        particle_str = "Electron"
    elif pid == 13:
        particle_str = "Muon"
    elif pid == 22:
        particle_str = "Gamma"
    else:
        particle_str = "Unknown"

    position = event_info["position"]
    direction = event_info["direction"]
    energy = event_info["energy"]
    geo = wcsim.geo
    num_pmts = geo.GetWCNumPMT()
    digi_hits = wcsim.get_digitized_hits()
    digi_hit_pmt = digi_hits["pmt"]
    digi_hit_time = digi_hits["time"]
    print("File name:",os.path.basename(input_file))
    print("Index of the event:", event_index)
    print("Number of triggers:", wcsim.ntrigger)
    print("Particle:", particle_str)
    print("Energy: {:.1f} MeV".format(energy))
    print("Position: ({:.1f}, {:.1f}, {:.1f}) cm".format(position[0], position[1], position[2]))
    print("Direction: ({:.2f}, {:.2f}, {:.2f})".format(direction[0], direction[1], direction[2]))

    time = np.zeros(num_pmts)
    for pmt, ch in zip(digi_hit_pmt, digi_hit_time):
        if pmt < num_pmts:
            time[pmt] = np.max([time[pmt], ch])

    sorted_indices = sorted(positions_dict.keys())
    positions_array = np.array([positions_dict[i] for i in sorted_indices])
    charges_ordered = np.array([time[i] for i in sorted_indices])
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(positions_array[:, 0], positions_array[:, 1], s=1, c=charges_ordered, cmap='viridis', marker='o')
    ax.set_title("Hyper-K Event Display".format(event_index),fontproperties=title_font)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = plt.colorbar(sc, ax=ax, label="time")
    cb.ax.yaxis.label.set_fontproperties(zaxi_font)
    info_text = (
    "Index of the event: {}\n"
    "Number of triggers: {}\n"
    "Particle: {}\n"
    "Energy: {:.1f} MeV\n"
    "Direction: ({:.2f}, {:.2f}, {:.2f})\n"
    "Position: ({:.1f}, {:.1f}, {:.1f}) cm"
).format( event_index, wcsim.ntrigger, particle_str, energy,
          direction[0], direction[1], direction[2],position[0], position[1], position[2])

    fig.text(0.53, 0.85,info_text, ha='left', va='top', fontproperties=info_font)


    fig.savefig(output_file)
    print("Static image saved as", output_file)

    return positions_dict










if __name__ == '__main__':
    config = get_args()
    input_file = os.path.abspath(config.input)
    event_index = config.event
    output_file = config.output
    if os.path.splitext(input_file)[1].lower() != '.root':
        print("File " + input_file + " is not a .root file")
        exit(1)
    positions_dict = plot_geo(input_file)
    if config.time:
        plot_time(event_index, input_file, positions_dict,output_file)
    else:
        plot_charge(event_index, input_file, positions_dict,output_file)



