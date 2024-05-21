from datetime import datetime
from pydantic import BaseModel, computed_field


class Result(BaseModel):
    command: str
    stdout: str
    stderr: str
    return_code: int
    dt: datetime = datetime.now()

    @computed_field
    @property
    def is_failed(self) -> bool:
        if self.stderr != '' or self.return_code != 0:
            return True

        return False
