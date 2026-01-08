#!/bin/bash
#SBATCH --partition=gpu_a100
#SBATCH --gpus=1
#SBATCH --ntasks=1
# SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH -o ./slurm_output/output/out_%j.log  
#SBATCH -e ./slurm_output/error/error_%j.log
#SBATCH --job-name=ANTs_nomask

module load 2025
module load Python/3.13.1-GCCcore-14.2.0

source /projects/0/prjs0830/envs/preprocessing_env/bin/activate

# pip install --upgrade pip
# pip install -r requirements.txt
# pip install antspyx

## Check GPU availability
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda); print(torch.__version__)"


python main.py \
    --input /projects/0/prjs0830/DATA/samples \
    --output /projects/0/prjs0830/DATA/samples_processed \
    --atlas ./atlas/mni_icbm152_t1_tal_nlin_sym_09a.nii.gz\
    --atlas_mask ./atlas/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii.gz\
    --reg_tool ANTs