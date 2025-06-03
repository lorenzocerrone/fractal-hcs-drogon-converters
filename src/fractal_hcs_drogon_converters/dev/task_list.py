"""Contains the list of tasks available to fractal."""

from fractal_task_tools.task_models import ConverterCompoundTask

AUTHORS = "Fractal Core Team"
DOCS_LINK = "https://github.com/lorenzocerrone/fractal-hcs-drogon-converters"
INPUT_MODELS = [
    (
        "fractal_hcs_drogon_converters",
        "convert_hcs_drogon_init_task.py",
        "DrogonPlateInputModel",
    ),
    (
        "fractal_hcs_drogon_converters",
        "convert_hcs_drogon_init_task.py",
        "AdvancedOptions",
    ),
]

TASK_LIST = [
    ConverterCompoundTask(
        name="Convert HCS Drogon Plate to OME-Zarr",
        executable_init="convert_hcs_drogon_init_task.py",
        executable="convert_hcs_drogon_compute_task.py",
        meta_init={"cpus_per_task": 1, "mem": 4000},
        meta={"cpus_per_task": 1, "mem": 12000},
        category="Conversion",
        modality="HCS",
        tags=[
            "Plate converter",
        ],
        docs_info="file:docs_info/convert_hcs_drogon_task.md",
    ),
]
