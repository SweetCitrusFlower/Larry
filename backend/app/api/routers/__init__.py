from fastapi import APIRouter

from . import auth, journeys, daily_plans, tasks, submissions, knowledge_sources

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(journeys.router, prefix="/journeys", tags=["journeys"])
api_router.include_router(daily_plans.router, prefix="/daily-plans", tags=["daily_plans"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(knowledge_sources.router, prefix="/knowledge-sources", tags=["knowledge_sources"])
