"""Training job domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class JobType(str, Enum):
    """Training job types."""

    LORA = "lora"
    QLORA = "qlora"
    MLIP_MACE = "mlip_mace"
    MLIP_NEQUIP = "mlip_nequip"
    GNN = "gnn"
    SELFIES_VAE = "selfies_vae"
    REINVENT = "reinvent"


class JobStatus(str, Enum):
    """Training job status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class HardwareProfile(str, Enum):
    """Hardware configuration for training."""

    CPU = "cpu"
    GPU = "gpu"
    MULTI_GPU = "multi-gpu"


@dataclass
class TrainingJob:
    """Model training job entity."""

    job_type: JobType
    base_model: str
    dataset_id: UUID
    hyperparameters: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.QUEUED
    checkpoint_path: Optional[str] = None
    metrics: dict[str, list[float]] = field(default_factory=dict)
    hardware_profile: HardwareProfile = HardwareProfile.CPU
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate training job data."""
        if not self.base_model:
            raise ValueError("Base model cannot be empty")
        if not self.hyperparameters:
            raise ValueError("Hyperparameters cannot be empty")


@dataclass
class ModelCheckpoint:
    """Model checkpoint entity."""

    training_job_id: UUID
    file_path: str
    epoch: int
    id: UUID = field(default_factory=uuid4)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate checkpoint data."""
        if not self.file_path:
            raise ValueError("Checkpoint file path cannot be empty")
        if self.epoch < 0:
            raise ValueError("Epoch must be non-negative")


@dataclass
class TrainingDataset:
    """Training dataset entity."""

    name: str
    dataset_type: str
    file_path: str
    id: UUID = field(default_factory=uuid4)
    record_count: int = 0
    schema: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate dataset data."""
        if not self.name:
            raise ValueError("Dataset name cannot be empty")
        if not self.dataset_type:
            raise ValueError("Dataset type cannot be empty")
        if not self.file_path:
            raise ValueError("Dataset file path cannot be empty")
