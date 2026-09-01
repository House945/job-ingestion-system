from fastapi import Request

from jobs.service import JobService


def get_service(request: Request) -> JobService:
    service: JobService = request.app.state.service
    return service
