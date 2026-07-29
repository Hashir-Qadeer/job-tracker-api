class JobNotFoundException(Exception):
    def __init__(self, job_id: int):
        self.job_id = job_id
        super().__init__(f"Job with id {job_id} not found")


class UnauthorizedException(Exception):
    pass


class DuplicateEmailException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email {email} already registered")


class InvalidCredentialsException(Exception):
    pass