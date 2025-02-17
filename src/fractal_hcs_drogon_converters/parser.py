from pathlib import Path

import numpy as np
import pandas
import tifffile
import yaml
from fractal_converters_tools.tile import Point, Tile, TileSpace, Vector
from fractal_converters_tools.tiled_image import PlatePathBuilder, TiledImage
from ngio.ngff_meta.fractal_image_meta import PixelSize


def find_channels_meta(acquisition_path: Path) -> dict[str, str]:
    # find all .yaml and .yml files in the acquisition folder
    yaml_files_path = list(acquisition_path.glob("*.yml")) + list(
        acquisition_path.glob("*.yaml")
    )
    if len(yaml_files_path) == 0:
        raise FileNotFoundError(
            "No channel metadata yaml file found in the acquisition folder"
        )

    if len(yaml_files_path) > 1:
        raise FileNotFoundError(
            "Multiple channel metadata yaml files found in the acquisition folder"
        )

    yaml_file_path = yaml_files_path[0]
    with open(yaml_file_path, "r") as file:
        yaml_data = yaml.load(file, Loader=yaml.SafeLoader)
    return yaml_data


def load_cell_line_layout(csv_path):
    cellline_layout = pandas.read_csv(csv_path)
    cellline_layout = cellline_layout.set_index(cellline_layout.columns[0], drop=True)

    cell_line_layout = {}
    for column in cellline_layout.columns:
        for row, cell_line in zip(
            cellline_layout[column].index, cellline_layout[column]
        ):
            int_column = int(column)
            if int_column < 10:
                column = f"0{int_column}"
            well = f"{row}{column}"
            if well in cell_line_layout:
                raise ValueError(
                    f"Duplicate well {well}, each well should only be present once in the cell line csv"
                )
            cell_line_layout[well] = {
                "row": row,
                "column": column,
                "cell_line": cell_line,
            }
    return cell_line_layout


def find_tiff_files(tiff_base_path):
    tiff_files = list(tiff_base_path.glob("*.tif"))

    if len(tiff_files) == 0:
        raise FileNotFoundError("No tiff files found in the acquisition folder")

    tiff_paths = {}
    for path in tiff_files:
        well = path.stem.split("_")[-2]
        if well not in tiff_paths:
            tiff_paths[well] = []
        tiff_paths[well].append(path)

    for paths in tiff_paths.values():
        paths.sort()
    return tiff_paths


class TiffLoader:
    """Load a full tile from a list of tiff images."""

    def __init__(self, tiff_paths: list[Path]):
        """Initialize the TiffLoader."""
        if not tiff_paths:
            raise ValueError("No tiff paths provided.")
        self.tiff_paths = tiff_paths

    def _open_tiff(self, path: Path) -> np.ndarray:
        """Open a tiff file."""
        try:
            im = tifffile.imread(path)[0]
            return im
        except Exception as e:
            raise ValueError(f"Error opening tiff file {path}: {e}") from e

    @property
    def tile_shape(self) -> tuple[int, int, int, int, int]:
        """Return the shape of the tile."""
        try:
            with tifffile.TiffFile(self.tiff_paths[0]) as tif:
                dimensions = tif.series[0].shape
            return (1, len(self.tiff_paths), 1, dimensions[1], dimensions[2])
        except Exception as e:
            return self._open_tiff(self.tiff_paths[0]).shape

    @property
    def dtype(self) -> np.dtype:
        """Return the dtype of the tiff files."""
        try:
            with tifffile.TiffFile(self.tiff_paths[0]) as tif:
                return tif.series[0].dtype
        except Exception as e:
            return self._open_tiff(self.tiff_paths[0]).dtype

    def load(self) -> np.ndarray:
        """Return the full tile."""
        im = self._open_tiff(self.tiff_paths[0])
        full_tile = np.zeros(shape=self.tile_shape, dtype=self.dtype)
        full_tile[0, 0, 0, :, :] = im

        for i, path in enumerate(self.tiff_paths[1:], start=1):
            im = self._open_tiff(path)
            full_tile[0, i, 0, :, :] = im
        return full_tile


def parse_drogon_metadata(
    acquisition_path: Path,
    csv_path: Path,
    acquisition_id: int = 0,
    plate_name: str = "test",
) -> list[TiledImage]:
    channel_dict = find_channels_meta(acquisition_path)

    tiff_base_path = acquisition_path / "TIF_OVR_MIP"
    tiff_files = find_tiff_files(tiff_base_path)
    cell_line_layout = load_cell_line_layout(csv_path)
    tiled_images = []
    for well, well_info in cell_line_layout.items():
        if well not in tiff_files:
            # print(f"No tiff files found for well {well}")
            continue

        tiff_loader = TiffLoader(tiff_files[well])
        tiled_image = TiledImage(
            name=well,
            path_builder=PlatePathBuilder(
                plate_name=plate_name,
                row=well_info["row"],
                column=int(well_info["column"]),
                acquisition_id=acquisition_id,
            ),
            channel_names=list(channel_dict.values()),
        )
        _, shape_c, _, shape_y, shape_x = tiff_loader.tile_shape
        tile = Tile(
            top_l=Point(0, 0, 0, 0, 0),
            diag=Vector(shape_x, shape_y, 1, c=shape_c, t=1),
            pixel_size=PixelSize(x=0.325, y=0.325, z=1),
            space=TileSpace.PIXEL,
            data_loader=tiff_loader,
        )
        tiled_image.add_tile(tile)
        tiled_images.append(tiled_image)
    return tiled_images
