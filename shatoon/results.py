from datetime import datetime

from pydantic import BaseModel, computed_field  # type: ignore


class Result(BaseModel):  # type: ignore
    command: str
    stdout: str
    stderr: str
    return_code: int
    dt: datetime = datetime.now()

    @computed_field  # type: ignore
    @property
    def is_failed(self) -> bool:
        if self.stderr != "" or self.return_code != 0:
            return True

        return False
