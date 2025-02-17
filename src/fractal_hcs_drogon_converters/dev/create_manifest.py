"""
Generate JSON schemas for task arguments afresh, and write them
to the package manifest.
"""

from fractal_tasks_core.dev.create_manifest import create_manifest

custom_pydantic_models = [
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

if __name__ == "__main__":
    PACKAGE = "fractal_hcs_drogon_converters"
    AUTHORS = "Lorenzo Cerrone"
    docs_link = "https://github.com/lorenzocerrone/fractal-hcs-drogon-converters"
    create_manifest(
        package=PACKAGE,
        authors=AUTHORS,
        docs_link=docs_link,
        custom_pydantic_models=custom_pydantic_models,
    )
