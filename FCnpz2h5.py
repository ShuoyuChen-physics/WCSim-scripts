"""
Modified by: Shuoyu Chen for HKFDML
"""
import numpy as np
import os
from datetime import datetime
import argparse
import h5py



def get_args():
    parser = argparse.ArgumentParser(description='convert and merge .npz files to hdf5')
    parser.add_argument('input_files', type=str, nargs='+')
    parser.add_argument('-o', '--output_file', type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    config = get_args()
    print("ouput file:", config.output_file)
    f = h5py.File(config.output_file, 'w')

    script_path = os.path.dirname(os.path.abspath(__file__))

    total_rows = 0
    total_hits = 0

    print("counting events and hits, in files")
    file_event_triggers = {}
    for input_file in config.input_files:
        print(input_file, flush=True)
        if not os.path.isfile(input_file):
            raise ValueError(input_file+" does not exist")
        npz_file = np.load(input_file, allow_pickle=True)
        event_ids = npz_file['used_event_id']
        digi_hit_pmt= npz_file['digi_hit_pmt']
        total_rows += event_ids.shape[0]
        for ev in range(total_rows):
            total_hits += len(digi_hit_pmt[ev])

    print(len(config.input_files), "files with", total_rows, "events with", total_hits, "hits")

    dset_labels = f.create_dataset("labels",
                                   shape=(total_rows,),
                                   dtype=np.int32)
    dset_PATHS = f.create_dataset("root_files",
                                  shape=(total_rows,),
                                  dtype=h5py.special_dtype(vlen=str))
    dset_IDX = f.create_dataset("event_ids",
                                shape=(total_rows,),
                                dtype=np.int32)
    dset_root_id = f.create_dataset("root_event_id",
                                shape=(total_rows,),
                                dtype=np.int32)                            
    dset_hit_time = f.create_dataset("hit_time",
                                     shape=(total_hits, ),
                                     dtype=np.float32)
    dset_hit_charge = f.create_dataset("hit_charge",
                                       shape=(total_hits, ),
                                       dtype=np.float32)
    dset_hit_pmt = f.create_dataset("hit_pmt",
                                    shape=(total_hits, ),
                                    dtype=np.int32)
    dset_event_hit_index = f.create_dataset("event_hits_index",
                                            shape=(total_rows,),
                                            dtype=np.int64)  # int32 is too small to fit large indices
    dset_energies = f.create_dataset("energies",
                                     shape=(total_rows, 1),
                                     dtype=np.float32)
    dset_positions = f.create_dataset("positions",
                                      shape=(total_rows, 1, 3),
                                      dtype=np.float32)
    dset_angles = f.create_dataset("angles",
                                   shape=(total_rows, 2),
                                   dtype=np.float32)

    offset = 0
    offset_next = 0
    hit_offset = 0
    hit_offset_next = 0
    label_map = {22: 0, 11: 1, 13: 2}
    for input_file in config.input_files:
        npz_file = np.load(input_file, allow_pickle=True)

        root_event_id = npz_file['root_event_id']
        event_ids = npz_file['used_event_id']
        root_files = npz_file['root_file']
        pids = npz_file['pid']
        positions = npz_file['position']
        directions = npz_file['direction']
        energies = npz_file['energy']
        hit_times = npz_file['digi_hit_time']
        hit_charges = npz_file['digi_hit_charge']
        hit_pmts = npz_file['digi_hit_pmt']

        offset_next += event_ids.shape[0]

        dset_IDX[offset:offset_next] = event_ids
        dset_root_id[offset:offset_next] = root_event_id
        dset_PATHS[offset:offset_next] = root_files
        dset_energies[offset:offset_next, :] = energies.reshape(-1, 1)
        dset_positions[offset:offset_next, :, :] = positions.reshape(-1, 1, 3)

        labels = np.full(pids.shape[0], -1)
        for k, v in label_map.items():
            labels[pids == k] = v
        dset_labels[offset:offset_next] = labels

        polars = np.arccos(directions[:, 1])
        azimuths = np.arctan2(directions[:, 2], directions[:, 0])
        dset_angles[offset:offset_next, :] = np.hstack((polars.reshape(-1, 1), azimuths.reshape(-1, 1)))

        for i, (times, charges, pmts) in enumerate(zip( hit_times, hit_charges, hit_pmts)):
            dset_event_hit_index[offset+i] = hit_offset

            hit_indices = np.arange(len(pmts))
            if len(hit_indices) > 0:
                hit_offset_next += len(hit_indices)
                dset_hit_time[hit_offset:hit_offset_next] = times[hit_indices]
                dset_hit_charge[hit_offset:hit_offset_next] = charges[hit_indices]
                dset_hit_pmt[hit_offset:hit_offset_next] = pmts[hit_indices]
            hit_offset = hit_offset_next

        offset = offset_next
    f.close()
    print("saved", hit_offset, "hits in", offset, "events")
