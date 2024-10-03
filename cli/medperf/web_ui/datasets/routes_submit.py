import uuid
from dataclasses import dataclass
from typing import Dict

from fastapi import Form, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from medperf.commands.dataset.submit import DataCreation
from medperf.entities.benchmark import Benchmark
from medperf.web_ui.common import templates


@dataclass
class _DatasetDraft:
    preparation: DataCreation
    submission_dict: dict
    draft_id: str


router = APIRouter()

_drafts: Dict[str, _DatasetDraft] = {}


@router.post("/draft/generate", response_class=JSONResponse)
async def generate_draft(
        benchmark: int = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        location: str = Form(...),
        data_path: str = Form(...),
        labels_path: str = Form(...)
):
    draft_id = str(uuid.uuid4())
    # Run the dataset creation logic using the CLI method
    preparation = DataCreation(
        benchmark_uid=benchmark,
        prep_cube_uid=None,
        data_path=data_path,
        labels_path=labels_path,
        metadata_path=None,  # metadata_path,
        name=name,
        description=description,
        location=location,
        approved=False,
        submit_as_prepared=False,
        for_test=False,
    )
    submission_dict = preparation.prepare_dict(False)
    draft = _DatasetDraft(
        preparation=preparation,
        submission_dict=submission_dict,
        draft_id=draft_id
    )
    _drafts[draft_id] = draft

    return {"data": draft.submission_dict, "draft_id": draft.draft_id}


@router.get("/draft/submit", response_class=RedirectResponse)
async def submit_draft(
        draft_id: str,
):
    draft = _drafts[draft_id]
    preparation = draft.preparation
    preparation.approved = True

    updated_dataset_dict = preparation.upload()
    preparation.to_permanent_path(updated_dataset_dict)
    preparation.write(updated_dataset_dict)
    dataset_id = updated_dataset_dict["id"]
    return RedirectResponse(f"/datasets/ui/display/{dataset_id}")


@router.get("/draft/decline", response_class=RedirectResponse)
async def decline_draft(draft_id: str):
    del _drafts[draft_id]
    return RedirectResponse("/datasets/ui")


@router.get("/ui/create", response_class=HTMLResponse)
def create_dataset_ui(request: Request):
    # Fetch the list of benchmarks to populate the benchmark dropdown
    benchmarks = Benchmark.all()
    # Render the dataset creation form with the list of benchmarks
    return templates.TemplateResponse("create_dataset.html", {"request": request, "benchmarks": benchmarks})
