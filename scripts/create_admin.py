from getpass import getpass

from pydantic import ValidationError

from app.core.exceptions import ResourceConflictError
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserRole
from app.services.user import UserService


def main() -> None:
    """Interactively create the first administrator."""

    print("Create EnterpriseFlow administrator")
    print("-----------------------------------")

    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ")
    password_confirmation = getpass("Confirm password: ")

    if password != password_confirmation:
        raise SystemExit("Passwords do not match")

    try:
        payload = UserCreate(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN,
        )

    except ValidationError as exc:
        raise SystemExit(f"Invalid administrator data:\n{exc}") from exc

    with SessionLocal() as db:
        try:
            user = UserService.create_user(
                db,
                payload,
            )

        except ResourceConflictError as exc:
            raise SystemExit(str(exc)) from exc

    print()
    print("Administrator created successfully")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")


if __name__ == "__main__":
    main()
