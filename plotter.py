import os
from os import path
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import glob
import matplotlib.colors

from pandas.core.frame import DataFrame

dir = path.dirname(__file__)
plots_dir = path.join(dir, 'plots')
results_dir = path.join(dir, 'results')
os.makedirs(path.join(dir, 'plots'), exist_ok=True)

def gflops_mm(mat_size): return 2 * (mat_size ** 3) * 1e-9
def gflops_lu(mat_size): return 2/3 * (mat_size ** 3) * 1e-9

def readExp(folder):
  newdf = [] 
  for name in glob.glob(path.join(results_dir, f'{folder}/*.csv')):
    newdf.append(pd.read_csv(name))
  frame = pd.concat(newdf, axis=0, ignore_index=True)
  frame = frame.drop('Exp', axis=1)
  return frame


lu_data_df = readExp('lu_data')
lu_func_df = readExp('lu_func')
lu_seq_df = readExp('lu_seq')
lu_sycl_cpu_df = readExp('lu_sycl_cpu')
lu_sycl_gpu_df = readExp('lu_sycl_gpu')
mm_cuda_df = readExp('mm_cuda')
mm_omp_df = readExp('mm_omp')
mm_sycl_cpu_df = readExp('mm_sycl_cpu')
mm_sycl_gpu_df = readExp('mm_sycl_gpu')


mm_omp_df['Performance'] = gflops_mm(mm_omp_df['Matrix Size']) / mm_omp_df['Time']
mm_cuda_df['Performance'] = gflops_mm(mm_cuda_df['Matrix Size']) / mm_cuda_df['Time']
mm_sycl_cpu_df['Performance'] = gflops_mm(mm_sycl_cpu_df['Matrix Size']) / mm_sycl_cpu_df['Time']
mm_sycl_gpu_df['Performance'] = gflops_mm(mm_sycl_gpu_df['Matrix Size']) / mm_sycl_gpu_df['Time']
lu_seq_df['Performance'] = gflops_mm(lu_seq_df['Matrix Size']) / lu_seq_df['Time']
lu_sycl_cpu_df['Performance'] = gflops_lu(lu_sycl_cpu_df['Matrix Size']) / lu_sycl_cpu_df['Time']
lu_sycl_gpu_df['Performance'] = gflops_lu(lu_sycl_gpu_df['Matrix Size']) / lu_sycl_gpu_df['Time']

colors = ['red', 'green', 'blue', 'cyan', 'magenta','yellow','lightsalmon', 'lightgreen', 'purple', 'purple']

# MM Seq ----------------------------------------------------------------------------------------
def plotMMSeq(df, x, y, xlabel, ylabel, legendTitle, op, p, destName, perBlock=True):

  group_by = ['Matrix Size', 'Block Size'] if perBlock else ['Matrix Size'] 
  mean = df[(df['Op'] == op) & (df['P'] == p) ].groupby(group_by, as_index=False).mean()

  if perBlock:
    for bs, color in zip([128, 256, 512], colors):
      plot = mean[mean['Block Size'] == bs]
      plt.plot(plot[x], plot[y],  '-x', color=color, label=str(bs))
      plt.legend(title=legendTitle)
  else:
      plt.plot(mean[x], mean[y],  '-x', color=colors[0])

  plt.ylabel(ylabel)
  plt.xlabel(xlabel)
  plt.ylim(bottom=0)
  plt.savefig(path.join(plots_dir, f'{destName}.png'))
  plt.cla()


plotMMSeq(mm_omp_df, 'Matrix Size', 'Time', 'Matrix Size', 'Time (s)', 'Block Size', 1, 1, 'mm_1_time')
plotMMSeq(mm_omp_df, 'Matrix Size', 'Performance', 'Matrix Size', 'Gflop/s', 'Block Size', 1, 1, 'mm_1_perf')

# LU Seq ----------------------------------------------------------------------------------------
group_by = ['Matrix Size', 'Block Size'] 
mean = lu_seq_df[(lu_seq_df['Op'] == 2) & (lu_seq_df['P'] == 1) ].groupby(group_by, as_index=False).mean()

for bs, color in zip([128, 256, 512], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'Blocked ({bs})')

group_by = ['Matrix Size'] 
mean = lu_seq_df[(lu_seq_df['Op'] == 1) & (lu_seq_df['P'] == 1) ].groupby(group_by, as_index=False).mean()
plt.plot(mean['Matrix Size'], mean['Time'],  '-x', color=colors[-1], label=f'Naive ({bs})')
plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_1_2_time.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = lu_seq_df[(lu_seq_df['Op'] == 2) & (lu_seq_df['P'] == 1) ].groupby(group_by, as_index=False).mean()

for bs, color in zip([128, 256, 512], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'Blocked ({bs})')

group_by = ['Matrix Size'] 
mean = lu_seq_df[(lu_seq_df['Op'] == 1) & (lu_seq_df['P'] == 1) ].groupby(group_by, as_index=False).mean()
plt.plot(mean['Matrix Size'], mean['Performance'],  '-x', color=colors[-1], label=f'Naive')
plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_1_2_perf.png'))
plt.cla()

# MM Cuda ----------------------------------------------------------------------------------------

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_cuda_df[(mm_cuda_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W Local Mem  ({bs})')

mean = mm_cuda_df[(mm_cuda_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W/o Local Mem ({bs})')

# plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_cuda_block_perf.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_cuda_df[(mm_cuda_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/ Local Mem  ({bs})')

mean = mm_cuda_df[(mm_cuda_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/o Local Mem ({bs})')

plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_cuda_block_time.png'))
plt.cla()

# MM Sycl CPU ----------------------------------------------------------------------------------------

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'Naive ({bs})')
group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W/o Local Mem  ({bs})')

mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[6:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W/ Local Mem ({bs})')

# plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_sycl_cpu_perf.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'Naive  ({bs})')
group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/o Local Mem  ({bs})')

mean = mm_sycl_cpu_df[(mm_sycl_cpu_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[6:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/ Local Mem ({bs})')

plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_sycl_cpu_time.png'))
plt.cla()

# MM Sycl GPU ----------------------------------------------------------------------------------------

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'Naive ({bs})')
group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W/o Local Mem  ({bs})')

mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[6:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'W/ Local Mem ({bs})')

# plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_sycl_gpu_perf.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'Naive  ({bs})')
group_by = ['Matrix Size', 'Block Size'] 
mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 2)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[3:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/o Local Mem  ({bs})')

mean = mm_sycl_gpu_df[(mm_sycl_gpu_df['Op'] == 3)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors[6:]):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'W/ Local Mem ({bs})')

plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'mm_sycl_gpu_time.png'))
plt.cla()

# LU Sycl CPU ----------------------------------------------------------------------------------------

group_by = ['Matrix Size', 'Block Size'] 
mean = lu_sycl_cpu_df[(lu_sycl_cpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'Naive ({bs})')
group_by = ['Matrix Size', 'Block Size'] 

plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_sycl_cpu_perf.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = lu_sycl_cpu_df[(lu_sycl_cpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'Blocked  ({bs})')

plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_sycl_cpu_time.png'))
plt.cla()

# MM Sycl GPU ----------------------------------------------------------------------------------------

group_by = ['Matrix Size', 'Block Size'] 
mean = lu_sycl_gpu_df[(lu_sycl_gpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Performance'],  '-x', color=color, label=f'Blocked ({bs})')

plt.legend(title='Operation')
plt.ylabel('Performance (Gflop/s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_sycl_gpu_perf.png'))
plt.cla()

group_by = ['Matrix Size', 'Block Size'] 
mean = lu_sycl_gpu_df[(lu_sycl_gpu_df['Op'] == 1)].groupby(group_by, as_index=False).mean()

for bs, color in zip([8, 16, 32], colors):
  plot = mean[mean['Block Size'] == bs]
  plt.plot(plot['Matrix Size'], plot['Time'],  '-x', color=color, label=f'Blocked  ({bs})')

plt.legend(title='Operation')
plt.ylabel('Time (s)')
plt.xlabel('Matrix Size')
plt.ylim(bottom=0)
plt.savefig(path.join(plots_dir, f'lu_sycl_gpu_time.png'))
plt.cla()



