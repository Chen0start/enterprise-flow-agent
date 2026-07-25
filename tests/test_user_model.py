from app.models.user import User


def test_user_table_name() -> None:
    assert User.__tablename__ == "users"


def test_user_table_columns() -> None:
    expected_columns = {
        "id",
        "username",
        "email",
        "password_hash",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    }

    actual_columns = set(User.__table__.columns.keys())

    assert actual_columns == expected_columns


def test_user_unique_fields() -> None:
    assert User.__table__.c.username.unique is True
    assert User.__table__.c.email.unique is True


def test_user_required_fields() -> None:
    assert User.__table__.c.username.nullable is False
    assert User.__table__.c.email.nullable is False
    assert User.__table__.c.password_hash.nullable is False
