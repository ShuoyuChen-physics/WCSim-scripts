"""
Python 3 script for processing a list of ROOT files into .npz files

To keep references to the original ROOT files, the file path is stored in the output.
An index is saved for every event in the output npz file corresponding to the event index within that ROOT file (ev).

Authors: Nick Prouse
"""

"""
Modified by: Shuoyu Chen for HKFDML
Note: This script now only works for one file at a time.

"""

import argparse
from root_file_utils import *

ROOT.gROOT.SetBatch(True)
'''
Basically, I use:
    /DAQ/TriggerNDigits/Threshold 60
    /DAQ/TriggerNDigits/Window 400
    /DAQ/TriggerNDigits/PreTriggerWindow -400
    /DAQ/TriggerNDigits/PostTriggerWindow +950
'''
VALID_HIT_TIME_MIN = 0 
VALID_HIT_TIME_MAX = 2000 # 2000ns for the entire info
MIN_HITS = 200
MAX_HIT_TIME_FOR_MIN_HIT = 400
OFFSET = 950 # Using trigger offset 950ns


# Filters 
# Note: good evevt: number of hits and trigger type.
#       FC: whether FC events. *Bug in WCSim now
#       Veto: whether muon/electron/gamma exit the tank
#       Veto2: whether muon/electron/gamma exit the tank (estimated energy)
USE_GOOD_EVENT_FILTER = True
USE_FC_FILTER = True
USE_VETO_FILTER = False
USE_VETO2_FILTER = False

RADIUS = 3240
HALF_HEIGHT = 3290

def get_args():
    parser = argparse.ArgumentParser(description='dump WCSim data into numpy .npz file')
    parser.add_argument('input_files', type=str)
    parser.add_argument('-d', '--output_dir', type=str, default=None)
    args = parser.parse_args()
    return args

def out_of_tank(pos):
    if (pos[0] ** 2 + pos[1] ** 2 > RADIUS ** 2) or (pos[2] < - HALF_HEIGHT or pos[2] > HALF_HEIGHT):
        return True
    return False

# Todo: Waste of memory, need to optimize
def dump_file(infile, outfile):
    
    wcsim = WCSimFile(infile)
    nevents = wcsim.nevent
    root_event_id = np.empty(nevents, dtype=np.int32)
    used_event_id = np.empty(nevents, dtype=np.int32)
    root_file = np.empty(nevents, dtype=object)

    pid = np.empty(nevents, dtype=np.int32)
    position = np.empty((nevents, 3), dtype=np.float64)
    direction = np.empty((nevents, 3), dtype=np.float64)
    energy = np.empty(nevents,dtype=np.float64)

    digi_hit_pmt = np.empty(nevents, dtype=object)
    digi_hit_charge = np.empty(nevents, dtype=object)
    digi_hit_time = np.empty(nevents, dtype=object)
    digi_hit_trigger = np.empty(nevents, dtype=object)
    valid_digi_hit_pmt = np.empty(nevents, dtype=object)
    valid_digi_hit_charge = np.empty(nevents, dtype=object)
    valid_digi_hit_time = np.empty(nevents, dtype=object)

    track_pid = np.empty(nevents, dtype=object)
    track_energy = np.empty(nevents, dtype=object)
    track_start_position = np.empty(nevents, dtype=object)
    track_stop_position = np.empty(nevents, dtype=object)
    track_boundary_kes = np.empty(nevents, dtype=object)
    track_boundary_types = np.empty(nevents, dtype=object)

    trigger_time = np.empty(nevents, dtype=object)
    trigger_type = np.empty(nevents, dtype=object)

    good_event_flag = np.empty(nevents, dtype=np.bool_)
    event_veto = np.empty(nevents, dtype=np.bool_)
    event_veto2 = np.empty(nevents, dtype=np.bool_)
    event_FC = np.empty(nevents, dtype=np.bool_)
    event_used = np.empty(nevents, dtype=np.bool_)
    used_event = 0

    for ev in range(wcsim.nevent):
        wcsim.get_event(ev)
        event_info = wcsim.get_event_info()
        pid[ev] = event_info["pid"]
        position[ev] = event_info["position"]
        direction[ev] = event_info["direction"]
        energy[ev] = event_info["momentum"]

        digi_hits = wcsim.get_digitized_hits()
        digi_hit_pmt[ev] = digi_hits["pmt"]
        digi_hit_charge[ev] = digi_hits["charge"]
        digi_hit_time[ev] = digi_hits["time"]
        digi_hit_trigger[ev] = digi_hits["trigger"]
        
        triggers = wcsim.get_triggers()
        trigger_time[ev] = triggers["time"]
        trigger_type[ev] = triggers["type"]

        # Check if good event
        good_triggers = np.where((trigger_type[ev] == 0) | (trigger_type[ev] == 3))[0]
        if len(good_triggers) == 0:
            good_event_flag[ev] = False
            valid_hits_mask = ((digi_hit_time[ev] < VALID_HIT_TIME_MAX) & (digi_hit_time[ev] > VALID_HIT_TIME_MIN))
            valid_digi_hit_pmt[ev] = digi_hit_pmt[ev][valid_hits_mask]
            valid_digi_hit_charge[ev] = digi_hit_pmt[ev][valid_hits_mask]
            valid_digi_hit_time[ev] = digi_hit_pmt[ev][valid_hits_mask]
        else:
            first_trigger = good_triggers[np.argmin(trigger_time[ev][good_triggers])]
            nhits = np.count_nonzero((digi_hit_trigger[ev] == first_trigger) & (digi_hit_time[ev] < OFFSET + MAX_HIT_TIME_FOR_MIN_HIT) & (digi_hit_time[ev] > OFFSET))
            
            valid_hits_mask = ((digi_hit_trigger[ev] == first_trigger) & (digi_hit_time[ev] < VALID_HIT_TIME_MAX) & (digi_hit_time[ev] > VALID_HIT_TIME_MIN))

            valid_digi_hit_pmt[ev] = digi_hit_pmt[ev][valid_hits_mask]
            valid_digi_hit_charge[ev] = digi_hit_charge[ev][valid_hits_mask]
            valid_digi_hit_time[ev] = digi_hit_time[ev][valid_hits_mask]

            if nhits < MIN_HITS:
                good_event_flag[ev] = False
            else:
                good_event_flag[ev] = True



        tracks = wcsim.get_tracks()
        track_pid[ev] = tracks["pid"]
        track_energy[ev] = tracks["energy"]
        track_start_position[ev] = tracks["start_position"]
        track_stop_position[ev] = tracks["stop_position"]
        track_boundary_kes[ev] = tracks["boundary_kes"]
        track_boundary_types[ev] = tracks["boundary_types"]

        for pids, energies, starts, stops, kes, types in zip(track_pid[ev],track_energy[ev],track_start_position[ev],track_stop_position[ev],track_boundary_kes[ev],track_boundary_types[ev]):
            muon_tracks = np.abs(pids) == 13
            electron_tracks = np.abs(pids) == 11
            gamma_tracks = np.abs(pids) == 22
            muons_above_threshold = muon_tracks & (energies > 166)
            electrons_above_threshold = electron_tracks & (energies > 2)
            gammas_above_threshold = gamma_tracks & (energies > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold | gammas_above_threshold
            outside_tank = out_of_tank(stops)
            event_veto[ev] = not (np.any(outside_tank & above_threshold))

            end_energy_estimate = energies - np.linalg.norm(stops - starts)*2
            muons_above_threshold = muon_tracks & (end_energy_estimate > 166)
            electrons_above_threshold = electron_tracks & (end_energy_estimate > 2)
            gammas_above_threshold = gamma_tracks & (end_energy_estimate > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold | gammas_above_threshold
            event_veto2[ev] = not (np.any(above_threshold & outside_tank))
            
            muons_exit_above_threshold = [np.any((t == 1) & (k > 166)) for t, k in zip(types[muon_tracks], kes[muon_tracks])]
            electrons_exit_above_threshold = [np.any((t == 1) & (k > 2)) for t, k in zip(types[electron_tracks], kes[electron_tracks])]
            gammas_exit_above_threshold = [np.any((t == 1) & (k > 2)) for t, k in zip(types[gamma_tracks], kes[gamma_tracks])]
            event_FC[ev] = not (np.any(muons_exit_above_threshold) or np.any(electrons_exit_above_threshold) or np.any(gammas_exit_above_threshold))

        root_event_id[ev] = ev
        root_file[ev] = infile
 
        event_used[ev] = (good_event_flag[ev] or USE_GOOD_EVENT_FILTER == False) and (event_FC[ev] or USE_FC_FILTER == False) and (event_veto[ev] or USE_VETO_FILTER == False) and (event_veto2[ev] or USE_VETO2_FILTER == False)

        if event_used[ev]:
            used_event_id[ev] = used_event
            used_event += 1
        else:
            used_event_id[ev] = -1


    recorded_root_event_id = np.empty(used_event, dtype=np.int32)
    recorded_used_event_id = np.empty(used_event, dtype=np.int32)
    recorded_root_file = np.empty(used_event, dtype=object)
    recorded_pid = np.empty(used_event, dtype=np.int32)
    recorded_position = np.empty((used_event, 3), dtype=np.float64)
    recorded_direction = np.empty((used_event, 3), dtype=np.float64)
    recorded_energy = np.empty(used_event,dtype=np.float64)
    recorded_digi_hit_pmt = np.empty(used_event, dtype=object)
    recorded_digi_hit_charge = np.empty(used_event, dtype=object)
    recorded_digi_hit_time = np.empty(used_event, dtype=object)

    for ev in range(wcsim.nevent):
        if event_used[ev]:
            recorded_root_event_id[used_event_id[ev]] = root_event_id[ev]
            recorded_used_event_id[used_event_id[ev]] = used_event_id[ev]
            recorded_root_file[used_event_id[ev]] = root_file[ev]
            recorded_pid[used_event_id[ev]] = pid[ev]
            recorded_position[used_event_id[ev]] = position[ev]
            recorded_direction[used_event_id[ev]] = direction[ev]
            recorded_energy[used_event_id[ev]] = energy[ev]
            recorded_digi_hit_pmt[used_event_id[ev]] = valid_digi_hit_pmt[ev]
            recorded_digi_hit_charge[used_event_id[ev]] = valid_digi_hit_charge[ev]
            recorded_digi_hit_time[used_event_id[ev]] = valid_digi_hit_time[ev]



    np.savez_compressed(outfile,
                        root_event_id=recorded_root_event_id,                        
                        used_event_id=recorded_used_event_id,
                        root_file=recorded_root_file,
                        pid=recorded_pid,
                        position=recorded_position,
                        direction=recorded_direction,
                        energy=recorded_energy,
                        digi_hit_pmt=recorded_digi_hit_pmt,
                        digi_hit_charge=recorded_digi_hit_charge,
                        digi_hit_time=recorded_digi_hit_time,
                        )
    print("Total events: ", nevents)
    print("Good events: ", np.sum(good_event_flag))
    print("FC events: ", np.sum(event_FC))
    print("Pass veto events: ", np.sum(event_veto))
    print("Pass veto2 events: ", np.sum(event_veto2))
    print("Used events: ", used_event)
    del wcsim


if __name__ == '__main__':

    config = get_args()
    if config.output_dir is not None:
        print("output directory: " + str(config.output_dir))
        if not os.path.exists(config.output_dir):
            print("                  (does not exist... creating new directory)")
            os.mkdir(config.output_dir)
        if not os.path.isdir(config.output_dir):
            raise argparse.ArgumentTypeError("Cannot access or create output directory" + config.output_dir)
    else:
        print("output directory not provided... output files will be in same locations as input files")

    input_file = config.input_files
    if os.path.splitext(input_file)[1].lower() != '.root':
        print("File " + input_file + " is not a .root file, skipping")
    
    input_file = os.path.abspath(input_file)
    if config.output_dir is None:
        output_file = os.path.splitext(input_file)[0] + '.npz'
    else:
        output_file = os.path.join(config.output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.npz')
    print("\nNow processing " + input_file)
    print("Outputting to " + output_file)
    dump_file(input_file, output_file)



