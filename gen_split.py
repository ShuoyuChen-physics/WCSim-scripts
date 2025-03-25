import h5py as h5
import numpy as np

infile = '/disk03/usr8/schen/workspace/HKFDML/MCstorage/testdataset/e_0_range2gev_5_test.h5'

train_ratio = 0.8
val_ratio = 0.1
test_ratio = 1 - train_ratio - val_ratio


f = h5.File(infile, 'r')
pid_flg = f['labels'][:]
print(len(pid_flg))
good_idx = np.argwhere(pid_flg != 0).flatten()
print(len(good_idx))
n_good = good_idx.shape[0]

train_num = int(n_good * train_ratio)

val_num = int(n_good * (val_ratio))
train_idxs = good_idx[val_num:train_num+val_num]
val_idxs = good_idx[0:val_num]
test_idxs = good_idx[train_num+val_num:]
print(train_idxs)
print(val_idxs)
print(test_idxs)
print(len(test_idxs))
print(len(val_idxs))
print(len(train_idxs))
print(len(train_idxs)+len(val_idxs)+len(test_idxs))

split_idxs = {'train_idxs': train_idxs, 'val_idxs': val_idxs, 'test_idxs': test_idxs}

outname = infile.replace('.h5', '.npz')

np.savez(outname, **split_idxs)