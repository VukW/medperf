import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import List
from fastapi import Request

from medperf.account_management import get_medperf_user_data
from medperf.entities.cube import Cube
from medperf.entities.dataset import Dataset
from medperf.web_ui.common import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ui", response_class=HTMLResponse)
def datasets_ui(request: Request, local_only: bool = False, mine_only: bool = False):
    filters = {}
    my_user_id = get_medperf_user_data()["id"]
    if mine_only:
        filters["owner"] = my_user_id
    datasets = Dataset.all(
        local_only=local_only,
        filters=filters,
    )

    datasets = sorted(datasets, key=lambda x: x.created_at, reverse=True)
    # sort by (mine recent) (mine oldish), (other recent), (other oldish)
    mine_datasets = [d for d in datasets if d.owner == my_user_id]
    other_datasets = [d for d in datasets if d.owner != my_user_id]
    datasets = mine_datasets + other_datasets
    return templates.TemplateResponse("datasets.html", {"request": request, "datasets": datasets})


@router.get("/ui/{dataset_id}", response_class=HTMLResponse)
def dataset_detail_ui(request: Request, dataset_id: int):
    dataset = Dataset.get(dataset_id)

    prep_cube = Cube.get(cube_uid=dataset.data_preparation_mlcube)
    prep_cube_name = prep_cube.name if prep_cube else "Unknown"
    return templates.TemplateResponse("dataset_detail.html",
                                      {"request": request, "dataset": dataset, "prep_cube_name": prep_cube_name})
