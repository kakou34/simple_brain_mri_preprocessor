#!/usr/bin/env python3

import os
import argparse
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


def plot_middle_slices(nifti_path, output_path):
    img = nib.load(nifti_path)
    data = img.get_fdata()

    x_mid = data.shape[0] // 2  # sagittal
    y_mid = data.shape[1] // 2  # coronal
    z_mid = data.shape[2] // 2  # axial

    sagittal = data[x_mid, :, :]
    coronal = data[:, y_mid, :]
    axial = data[:, :, z_mid]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(np.rot90(sagittal), cmap="gray")
    axes[0].set_title("Sagittal")
    axes[0].axis("off")

    axes[1].imshow(np.rot90(coronal), cmap="gray")
    axes[1].set_title("Coronal")
    axes[1].axis("off")

    axes[2].imshow(np.rot90(axial), cmap="gray")
    axes[2].set_title("Axial")
    axes[2].axis("off")

    fig.suptitle(os.path.basename(nifti_path))
    plt.tight_layout()

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(input_folder, output_folder):
    if not os.path.isdir(input_folder):
        raise ValueError(f"{input_folder} is not a valid directory")

    os.makedirs(output_folder, exist_ok=True)

    nifti_files = sorted(
        f for f in os.listdir(input_folder)
        if f.endswith(".nii") or f.endswith(".nii.gz")
    )

    if not nifti_files:
        print("No NIfTI files found.")
        return

    for fname in nifti_files:
        nifti_path = os.path.join(input_folder, fname)

        base = fname.replace(".nii.gz", "").replace(".nii", "")
        out_png = os.path.join(output_folder, f"{base}.png")

        print(f"Saving {out_png}")
        plot_middle_slices(nifti_path, out_png)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Save middle sagittal, coronal, axial MRI slices as PNG"
    )

    parser.add_argument(
        "--input_folder",
        required=True,
        type=str,
        help="Path to folder containing .nii or .nii.gz files"
    )

    parser.add_argument(
        "--output_folder",
        required=True,
        type=str,
        help="Path to folder where PNGs will be saved"
    )

    args = parser.parse_args()
    main(args.input_folder, args.output_folder)
