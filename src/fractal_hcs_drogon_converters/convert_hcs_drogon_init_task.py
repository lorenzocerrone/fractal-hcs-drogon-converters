"""ScanR to OME-Zarr conversion task initialization."""

import logging
from pathlib import Path

from fractal_converters_tools.omezarr_plate_writers import initiate_ome_zarr_plates
from fractal_converters_tools.task_common_models import (
    AdvancedComputeOptions,
)
from fractal_converters_tools.task_init_tools import build_parallelization_list
from pydantic import BaseModel, Field, validate_call

from fractal_hcs_drogon_converters.parser import parse_drogon_metadata

logger = logging.getLogger(__name__)


class DrogonPlateInputModel(BaseModel):
    """Acquisition metadata.

    Attributes:
        path (str): Path to the Drgon acquisition.
        plate_name (str): Optional name of the plate.
            If not provided, the plate name will be inferred from the
            lif file + scan name.
            If the tile scan name is not provided, this field can not be
            used.
        acquisition_id: Acquisition ID, used to identify multiple rounds
            of acquisitions for the same plate.
            If tile_scan_name is not provided, this field can not be used.
    """

    path: str
    plate_name: str
    acquisition_id: int = Field(default=0, ge=0)


class AdvancedOptions(AdvancedComputeOptions):
    """Advanced options for the conversion.

    Attributes:
        num_levels (int): The number of resolution levels in the pyramid.
        tiling_mode (Literal["auto", "grid", "free", "none"]): Specify the tiling mode.
            "auto" will automatically determine the tiling mode.
            "grid" if the input data is a grid, it will be tiled using snap-to-grid.
            "free" will remove any overlap between tiles using a snap-to-corner
            approach.
            "none" will write the positions as is, using the microscope metadata.
        swap_xy (bool): Swap x and y axes coordinates in the metadata. This is sometimes
            necessary to ensure correct image tiling and registration.
        invert_x (bool): Invert x axis coordinates in the metadata. This is
            sometimes necessary to ensure correct image tiling and registration.
        invert_y (bool): Invert y axis coordinates in the metadata. This is
            sometimes necessary to ensure correct image tiling and registration.
        max_xy_chunk (int): XY chunk size is set as the minimum of this value and the
            microscope tile size.
        z_chunk (int): Z chunk size.
        c_chunk (int): C chunk size.
        t_chunk (int): T chunk size.
    """


@validate_call
def convert_hcs_drogon_init_task(
    *,
    # Fractal parameters
    zarr_urls: list[str],
    zarr_dir: str,
    # Task parameters
    acquisitions: list[DrogonPlateInputModel],
    cellline_layout_path: str,
    pixel_size_um: float = 0.325,
    overwrite: bool = False,
    advanced_options: AdvancedOptions = AdvancedOptions(),  # noqa: B008
):
    """Initialize the LIF Plate to OME-Zarr conversion task.

    Args:
        zarr_urls (list[str]): List of Zarr URLs.
        zarr_dir (str): Directory to store the Zarr files.
        acquisitions (list[AcquisitionInputModel]): List of raw acquisitions to convert
            to OME-Zarr.
        cellline_layout_path (str): Path to the cell line layout csv file.
        pixel_size_um (float): Pixel size in micrometers.
        overwrite (bool): Overwrite existing Zarr files.
        advanced_options (AdvancedOptions): Advanced options for the conversion.
    """
    path_cellline_layout = Path(cellline_layout_path)
    if not path_cellline_layout.exists():
        raise FileNotFoundError(f"Path {path_cellline_layout} does not exist.")

    tiled_images = []
    for acquisition in acquisitions:
        if not Path(acquisition.path).exists():
            raise FileNotFoundError(f"Path {acquisition.path} does not exist.")

        _tiled_images = parse_drogon_metadata(
            acquisition_path=Path(acquisition.path),
            csv_path=path_cellline_layout,
            acquisition_id=acquisition.acquisition_id,
            plate_name=acquisition.plate_name,
            pixel_size_um=pixel_size_um,
        )

        tiled_images.extend(_tiled_images)

    logger.info(f"Found {len(tiled_images)} tiled images.")

    parallelization_list = build_parallelization_list(
        zarr_dir=zarr_dir,
        tiled_images=tiled_images,
        overwrite=overwrite,
        advanced_options=advanced_options,
    )
    initiate_ome_zarr_plates(zarr_urls=zarr_urls, tiled_images=tiled_images)
    logger.info(f"Initialized {len(parallelization_list)} parallelization tasks.")
    return {"parallelization_list": parallelization_list}


if __name__ == "__main__":
    from fractal_tasks_core.tasks._utils import run_fractal_task

    run_fractal_task(
        task_function=convert_hcs_drogon_init_task, logger_name=logger.name
    )
