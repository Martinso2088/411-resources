from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    Class representing a boxer's basic information and statistics.

    Attributes:
        id (int): A unique identifier for the boxer.
        name (str): The name of the boxer.
        weight (int): The weight of the boxer in pounds.
        height (int): The height of the boxer in inches.
        reach (float): The reach of the boxer in inches.
        age (int): The age of the boxer.
        weight_class (str): The weight class of the boxer, which is automatically assigned based on weight.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """
    Function that creates a new boxer and adds them to the database.

    Args:
        name (str): The name of the boxer.
        weight (int): The weight of the boxer in pounds.
        height (int): The height of the boxer in inches.
        reach (float): The reach of the boxer in inches.
        age (int): The age of the boxer.

    Raises:
        ValueError: If the weight is less than 125, height or reach is less than or equal to 0, or if the weight is not between 18-40
        ValueError: If the boxer with the same name already exists in the database.
        sqlite3.Error: If there is an error with the database operation.
    """

    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

    except sqlite3.IntegrityError:
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """
    Function that deletes a boxer from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer that will be deleted.
    
    Raises:
        ValueError: If given ID of the boxer does not exist in the database.
        sqlite3.Error: If there is an error with the database operation.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Function that retrieves the leaderboard of boxers, which can be sorted by either wins or win percentage.

    Args:
        sort_by (str): The criteria to sort the leaderboard. Can be 'wins' or 'win_pct'(win percentage), although the default is 'wins'.
    
    Returns:
        List[dict[str, Any]]: A list of boxers containing their statistics

    Raises:
        ValueError: If the sort_by parameter is not 'wins' or 'win_pct'.
        sqlite3.Error: If there is an error with the database operation.
    """
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Function that retrieves a boxer's information from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer.

    Returns:
        Boxer: An instance of the Boxer class containing the boxer's information.

    Raises:
        ValueError: If the boxer with the given ID does not exist in the database.
        sqlite3.Error: If there is an error with the database operation.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Function that retrieves a boxer's information from the database by their name.

    Args:
        boxer_name (str): The name of the boxer.

    Returns:
        Boxer: An instance of the Boxer class containing the boxer's information.

    Raises:
        ValueError: If the boxer with the given name does not exist in the database.
        sqlite3.Error: If there is an error with the database operation.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """
    Function that determines the weight class of a boxer based on their weight.

    Args:
        weight (int): The weight of the boxer in pounds.

    Returns:
        str: The weight class of the boxer.

    Raises:
        ValueError: If the weight is less than 125.
    """
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Function that updates a boxer's statistics after they complete a fight.

    Args:
        boxer_id (int): The ID of the boxer.
        result (str): The result of the fight, which can be either 'win' or 'loss'.
    
    Raises:
        ValueError: If the result is not 'win' or 'loss', or if the boxer with the given ID does not exist in the database.
        sqlite3.Error: If there is an error with the database operation.
    """
    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
