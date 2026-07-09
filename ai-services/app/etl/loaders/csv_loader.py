"""AgroVision AI — Loader de CSVs procesados."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import pandas as pd

from app.infrastructure.persistence.dataset_storage import DatasetStorage


def load_master_dataset() -> pd.DataFrame:
    from app.config.constants import FEATURES_PATH
    return DatasetStorage.load(f"{FEATURES_PATH}/dataset_maestro.csv")


def load_eva_clean() -> pd.DataFrame:
    from app.config.constants import PROCESSED_PATH
    return DatasetStorage.load(f"{PROCESSED_PATH}/eva_clean.csv")
