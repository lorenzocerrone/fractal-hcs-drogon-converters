# fractal-hcs-drogon-converters

## Local installation

* Clone the repository
* Install the dependencies

```bash
pip install -e .
```

## Sample usage (in python)

```python
from fractal_hcs_drogon_converters.convert_hcs_drogon_compute_task import (
    convert_hcs_drogon_compute_task,
)
from fractal_hcs_drogon_converters.convert_hcs_drogon_init_task import (
    DrogonPlateInputModel,
    convert_hcs_drogon_init_task,
)

csv_path = "/Users/locerr/data/20250217_testdata_manuel/cellline_layout.csv"
acquisition_path = "/Users/locerr/data/20250217_testdata_manuel/D2_R1"
yaml_name = "name.yaml"

parallelization_list = convert_hcs_drogon_init_task(
    zarr_urls=[],
    zarr_dir="output-ome-zarr",
    acquisitions=[DrogonPlateInputModel(
        path=acquisition_path,
        yaml=yaml_name
        plate_name="Day2",
        acquisition_id=0)
    ],
    cellline_layout_path=csv_path,
    overwrite=True
)


for parallel_kwargs in parallelization_list["parallelization_list"]:
    convert_hcs_drogon_compute_task(zarr_url=parallel_kwargs["zarr_url"],
                                    init_args=parallel_kwargs["init_args"])
```
