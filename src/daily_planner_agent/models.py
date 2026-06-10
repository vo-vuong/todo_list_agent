from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Priority = Literal["low", "medium", "high"]


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""
    due_date: date
    estimated_minutes: int = Field(gt=0)
    priority: Priority
    completed: bool = False


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = ""
    due_date: date
    estimated_minutes: int = Field(gt=0)
    priority: Priority = "medium"


class ScheduleBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    priority: Priority
    start_time: time
    end_time: time
    notes: str = ""

    @model_validator(mode="after")
    def validate_time_order(self) -> "ScheduleBlock":
        if self.end_time <= self.start_time:
            raise ValueError("Schedule block end_time must be after start_time.")
        return self


class OverflowTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    priority: Priority
    reason: str = Field(min_length=1)


class DailyPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_date: date
    summary: str = Field(min_length=1)
    time_blocks: list[ScheduleBlock] = Field(default_factory=list)
    unscheduled_overflow: list[OverflowTask] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_workday_constraints(self) -> "DailyPlan":
        workday_start = time(9, 0)
        lunch_start = time(12, 0)
        lunch_end = time(13, 0)
        workday_end = time(17, 0)

        for block in self.time_blocks:
            if block.start_time < workday_start or block.end_time > workday_end:
                raise ValueError("Schedule blocks must stay within 09:00-17:00.")
            overlaps_lunch = block.start_time < lunch_end and block.end_time > lunch_start
            if overlaps_lunch:
                raise ValueError("Schedule blocks must not overlap lunch from 12:00-13:00.")

        ordered_blocks = sorted(self.time_blocks, key=lambda block: block.start_time)
        for previous, current in zip(ordered_blocks, ordered_blocks[1:]):
            if current.start_time < previous.end_time:
                raise ValueError("Schedule blocks must not overlap.")
        return self
