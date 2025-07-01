from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from poshub_api.demo.exceptions import ExternalDemoException
from poshub_api.demo.service import DemoService

router = APIRouter()


@router.get("/demo/external-demo")
async def external_demo(service: Annotated[DemoService, Depends(DemoService)]):
    try:
        response = await service.external_demo()
        return response
    except ExternalDemoException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
