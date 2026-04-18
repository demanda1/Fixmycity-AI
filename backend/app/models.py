from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class IssueCategory(str, Enum):
    POTHOLE = "pothole"
    GARBAGE = "garbage"
    DRAIN = "drain"
    STREETLIGHT = "streetlight"
    ROAD_DAMAGE = "road_damage"
    OTHER = "other"

class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueStatus(str, Enum):
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class ComplaintCreate(BaseModel):
    description: str = Field(..., min_length=10, max_length=500, example="Large pothole near bus stop causing accidents")
    latitude: float = Field(..., ge=-90, le=90, example=17.385044)
    longitude: float = Field(..., ge=-180, le=180, example=78.486671)
    ward: Optional[str] = Field(None, example="Banjara Hills - Ward 8")
    city: str = Field(..., example="Hyderabad")
    reporter_name: str = Field(..., min_length=2, example="Adam Kumar")
    reporter_email: str = Field(..., pattern=r"^[\w\.\-]+@[\w\.\-]+\.\w+$", example="adam.kumar@gmail.com")


class ComplaintResponse(BaseModel):
    id: int
    description: str
    category: IssueCategory
    severity: IssueSeverity
    status: IssueStatus
    latitude: float
    longitude: float
    ward: Optional[str]
    city: str
    reporter_name: str
    reporter_email: str
    created_at: str