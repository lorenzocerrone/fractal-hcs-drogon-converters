"""Contains the list of tasks available to fractal."""

from fractal_tasks_core.dev.task_models import CompoundTask

TASK_LIST = [
    CompoundTask(
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
