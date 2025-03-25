import argparse
from root_file_utils import *
from pos_utils_hyperk_mpmt import *

ROOT.gROOT.SetBatch(True)
'''
Basically, I use:
    /DAQ/TriggerNDigits/Threshold 30
    /DAQ/TriggerNDigits/Window 200
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
#       FC: whether FC events.
#       Veto: whether muon/electron/gamma exit the tank
#       Veto2: whether muon/electron/gamma exit the tank (estimated energy)

USE_GOOD_EVENT_FILTER = True
USE_FC_FILTER = True
USE_VETO_FILTER = False
USE_VETO2_FILTER = False
ANALYSIS_PID = 1 
RADIUS = 3240
HALF_HEIGHT = 3290

def get_args():
    parser = argparse.ArgumentParser(description='analysis of fitqun file')
    parser.add_argument('input_files', type=str)
    parser.add_argument('-f', '--fitqun_file', type=str, default=None)
    parser.add_argument('-o', '--output_file', type=str, default=None)
    args = parser.parse_args()
    return args

def out_of_tank(pos):
    if (pos[0] ** 2 + pos[1] ** 2 > RADIUS ** 2) or (pos[2] < - HALF_HEIGHT or pos[2] > HALF_HEIGHT):
        return True
    return False




# Todo: Waste of memory, need to optimize
def dump_file(infile):
    
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

    print("Total events: ", nevents)
    print("Good events: ", np.sum(good_event_flag))
    print("FC events: ", np.sum(event_FC))
    print("Pass veto events: ", np.sum(event_veto))
    print("Pass veto2 events: ", np.sum(event_veto2))
    print("Used events: ", used_event)
    del wcsim


    return event_used, position, direction, energy

ANALYSIS_PID = 1 

def fq_analysis(input,pid):
    file = ROOT.TFile.Open(input, "READ")
    tree = file.Get("fiTQun")


    fqnse_list = []
    fq1rmom_list = []
    fq1rpos_list = []
    fq1rdir_list = []
    num_events = tree.GetEntries()
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        fqnse_list.append(tree.fqnse)
        fq1rmom_list.append(np.array(tree.fq1rmom))
        fq1rpos_list.append(np.array(tree.fq1rpos))  
        fq1rdir_list.append(np.array(tree.fq1rdir))

    file.Close()

    if pid > 4:
        print("Invalid pid")
        return
    


    fq1rmom = np.zeros(num_events,dtype = np.float32)
    fq1rpos = np.zeros((num_events, 3), dtype = np.float32)
    fq1rdir = np.zeros((num_events, 3), dtype = np.float32)
    for i in range(num_events):
        fq1rmom[i] = fq1rmom_list[i][pid]
        for j in range(3):
            fq1rpos[i][j] = fq1rpos_list[i][pid * 3 + j]
            fq1rdir[i][j] = fq1rdir_list[i][pid * 3 + j]
    return fq1rpos, fq1rdir, fq1rmom 


if __name__ == '__main__':

    config = get_args()
    if config.fitqun_file is not None:
        print("fitqun file: " + str(config.fitqun_file))
    else:
        print("fitqun file not provided... output files will be in same locations as input files")

    input_file = config.input_files
    fitqun_file = config.fitqun_file
    output_file = config.output_file
    if os.path.splitext(input_file)[1].lower() != '.root':
        print("File " + input_file + " is not a .root file, skipping")



    event_used, true_position, true_direction, true_energy = dump_file(input_file)
    rec_position, rec_direction, rec_energy = fq_analysis(fitqun_file, ANALYSIS_PID)

    print(event_used)
    print(true_position[0])
    print(true_direction[0])
    print(true_energy[0])
    print(rec_position[0])
    print(rec_direction[0])
    print(rec_energy[0])
    np.savez(output_file,
             event_used=event_used,
             true_position=true_position,
             true_direction=true_direction,
             true_energy=true_energy,
             rec_position=rec_position,
             rec_direction=rec_direction,
             rec_energy=rec_energy)






