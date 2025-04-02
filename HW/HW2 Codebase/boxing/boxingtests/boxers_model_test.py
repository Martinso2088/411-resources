import pytest
import sqlite3
from boxing.boxing.models.boxers_model import (
    create_boxer, delete_boxer, get_leaderboard, 
    get_boxer_by_id, get_boxer_by_name, get_weight_class, update_boxer_stats
)
from boxing.utils.sql_utils import get_db_connection

@pytest.fixture
def mock_db(mocker):
    """Mock database connection and cursor."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mock_conn.cursor.return_value

    mocker.patch("boxing.utils.sql_utils.get_db_connection", return_value=mock_conn)
    return mock_cursor


##############################################
# Tests for Boxer Creation
##############################################

def test_create_boxer_success(mock_db):
    """Test successful boxer creation."""
    mock_db.fetchone.return_value = None  # Boxer does not already exist

    create_boxer(name="Mike Tyson", weight=220, height=71, reach=71, age=25)

    mock_db.execute.assert_any_call(
        "SELECT 1 FROM boxers WHERE name = ?", ("Mike Tyson",)
    )
    mock_db.execute.assert_any_call(
        "INSERT INTO boxers (name, weight, height, reach, age) VALUES (?, ?, ?, ?, ?)", 
        ("Mike Tyson", 220, 71, 71, 25)
    )


@pytest.mark.parametrize("weight", [124, 50])
def test_create_boxer_invalid_weight(mock_db, weight):
    """Test boxer creation fails due to invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight"):
        create_boxer(name="Light Boxer", weight=weight, height=65, reach=70, age=30)


@pytest.mark.parametrize("age", [17, 41])
def test_create_boxer_invalid_age(mock_db, age):
    """Test boxer creation fails due to age restrictions."""
    with pytest.raises(ValueError, match="Invalid age"):
        create_boxer(name="Old Boxer", weight=150, height=65, reach=70, age=age)


def test_create_duplicate_boxer(mock_db):
    """Test that creating a boxer with an existing name raises an error."""
    mock_db.fetchone.return_value = (1,)  # Boxer already exists

    with pytest.raises(ValueError, match="already exists"):
        create_boxer(name="Ali", weight=200, height=70, reach=74, age=28)


##############################################
# Tests for Fetching Boxers
##############################################

def test_get_boxer_by_id_success(mock_db):
    """Test fetching a boxer by ID."""
    mock_db.fetchone.return_value = (1, "Ali", 200, 70, 74, 28)

    boxer = get_boxer_by_id(1)

    assert boxer.name == "Ali"
    assert boxer.weight == 200
    assert boxer.height == 70
    assert boxer.reach == 74
    assert boxer.age == 28


def test_get_boxer_by_id_not_found(mock_db):
    """Test fetching a non-existent boxer by ID."""
    mock_db.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_id(99)


def test_get_boxer_by_name_success(mock_db):
    """Test fetching a boxer by name."""
    mock_db.fetchone.return_value = (1, "Ali", 200, 70, 74, 28)

    boxer = get_boxer_by_name("Ali")

    assert boxer.name == "Ali"
    assert boxer.weight == 200


def test_get_boxer_by_name_not_found(mock_db):
    """Test fetching a non-existent boxer by name."""
    mock_db.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_name("Unknown")


##############################################
# Tests for Leaderboard
##############################################

def test_get_leaderboard_sorted_by_wins(mock_db):
    """Test retrieving the leaderboard sorted by wins."""
    mock_db.fetchall.return_value = [
        (1, "Ali", 200, 70, 74, 28, 10, 8, 0.8),
        (2, "Tyson", 220, 71, 71, 25, 15, 10, 0.67)
    ]

    leaderboard = get_leaderboard(sort_by="wins")

    assert leaderboard[0]["name"] == "Tyson"  # More wins
    assert leaderboard[1]["name"] == "Ali"


def test_get_leaderboard_invalid_sort_by(mock_db):
    """Test leaderboard with invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter"):
        get_leaderboard(sort_by="unknown")


##############################################
# Tests for Weight Class
##############################################

@pytest.mark.parametrize("weight, expected_class", [
    (220, "HEAVYWEIGHT"),
    (170, "MIDDLEWEIGHT"),
    (140, "LIGHTWEIGHT"),
    (130, "FEATHERWEIGHT"),
])
def test_get_weight_class(weight, expected_class):
    """Test correct weight class assignment."""
    assert get_weight_class(weight) == expected_class


def test_get_weight_class_invalid():
    """Test weight class determination fails for low weights."""
    with pytest.raises(ValueError, match="Invalid weight"):
        get_weight_class(120)


##############################################
# Tests for Updating Boxer Stats
##############################################

def test_update_boxer_stats_win(mock_db):
    """Test updating a boxer's stats after a win."""
    mock_db.fetchone.return_value = (1,)  # Boxer exists

    update_boxer_stats(1, "win")

    mock_db.execute.assert_any_call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))


def test_update_boxer_stats_loss(mock_db):
    """Test updating a boxer's stats after a loss."""
    mock_db.fetchone.return_value = (1,)  # Boxer exists

    update_boxer_stats(1, "loss")

    mock_db.execute.assert_any_call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))


def test_update_boxer_stats_invalid_result(mock_db):
    """Test updating stats with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result"):
        update_boxer_stats(1, "draw")


def test_update_boxer_stats_nonexistent(mock_db):
    """Test updating stats for a non-existent boxer."""
    mock_db.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        update_boxer_stats(99, "win")


##############################################
# Tests for Deleting Boxers
##############################################

def test_delete_boxer_success(mock_db):
    """Test deleting a boxer by ID."""
    mock_db.fetchone.return_value = (1,)  # Boxer exists

    delete_boxer(1)

    mock_db.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))


def test_delete_boxer_not_found(mock_db):
    """Test deleting a non-existent boxer."""
    mock_db.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        delete_boxer(99)
