from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


def main() -> None:
    """Check the PostgreSQL connection and display existing tables."""

    try:
        with engine.connect() as connection:
            database_name, database_user = connection.execute(
                text("SELECT current_database(), current_user")
            ).one()

        table_names = inspect(engine).get_table_names()

    except SQLAlchemyError as exc:
        raise SystemExit(f"Database connection failed: {exc}") from exc

    print(f"Connected database: {database_name}")
    print(f"Connected user: {database_user}")
    print(f"Existing tables: {table_names}")


if __name__ == "__main__":
    main()