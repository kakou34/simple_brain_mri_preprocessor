# Simple Brain MRI Preprocessor

## Introduction

This repository contains a simple and modular pipeline to preprocess structural brain MRI (T1-weighted) images.  
The preprocessing consists of the following steps:

1. **Brain extraction** using **HD-BET**
2. **N4 bias field correction**
3. **Linear registration** to a reference atlas using **FSL FLIRT**

The pipeline is designed for batch processing of `.nii.gz` T1-weighted MRI scans and can run on CPU or GPU (for HD-BET).

---

## Requirements

### System dependencies

- **FSL** (required for FSL-based registration)

FSL must be installed **separately** and available in your environment.  
Installation instructions are available here:

👉 https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation

Make sure that:
```bash
FSLDIR is set and $FSLDIR/bin is in your PATH
```

### Python dependencies

The required Python packages are listed in requirements.txt and include:
- nibabel
- torch
- numpy
- HD-BET
You can install them using:
```
pip install -r requirements.txt
```
⚠️ Note: If you plan to use GPU acceleration for HD-BET, make sure your PyTorch installation matches your CUDA version.

## Usage
The main entry point of the pipeline is `main.py`

### Command line arguments
```
--input        Folder containing raw T1w .nii.gz files (required)
--output       Folder where final results will be saved (required)
--atlas        Fixed image for registration (e.g., MNI152 template) (required)
--atlas_mask   Brain mask of the fixed image (required)

--use_mask     Use brain masks during registration
--cleanup      Remove temporary files after processing
--device       Device to use for HD-BET: cuda or cpu (default: cuda)
```
### Example command

```
python main.py \
  --input /path/to/raw_t1s \
  --output /path/to/preprocessed \
  --atlas /path/to/MNI152_T1_1mm.nii.gz \
  --atlas_mask /path/to/MNI152_T1_1mm_brain_mask.nii.gz \
  --reg_tool FSL \
  --use_mask \
  --cleanup \
  --device cuda
```

## Containerization
An Apptainer recipe (`container/recipe.def`) s provided to build a containerized version of the pipeline with GPU support.
This is the recommended way to run the pipeline on HPC systems.

### Build the container 
```
apptainer build mri_preproc.sif container/recipe.def
```
⚠️ Note: the Apptainer image was optimized to ~9Gb (compared to 13Gb of the previous release v1.0)

### Run the container
```
apptainer run --nv \
    --bind /path/to/data/folder:/mnt/data \
    --bind /path/to/atlas:/atlas \
    brain_preproc.sif \
        --input /mnt/data/T1 \
        --output /mnt/data/Preprocessed \
        --atlas /atlas/mni_icbm152_t1_tal_nlin_sym_09a.nii.gz \
        --atlas_mask /atlas/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii.gz \
        --reg_tool FSL \
        --device cuda
```
### Public image
A built image is provided on Github Container Registry under: `ghcr.io/kakou34/sbmp-bigr:v2.0`


# Final Remarks 
- This repository represents a stable working release of a brain preprocessing pipeline.
- Compared to release v1.0, we aimed to optimize the size of the container by removing ANTsPy (thus restricting the registation to FSL) and improving the Apptainer recipe.
- For reproducibility, users are encouraged to use tagged releases
- If you use this code in your research, please cite this repo and the relevant tools (HD-BET, FSL).


