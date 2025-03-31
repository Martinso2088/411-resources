# === ring_model.py (with docstrings and logging) ===

import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)

class RingModel:
    """Model for managing boxing matches between two boxers."""

    def __init__(self):
        """Initializes the ring as an empty list."""
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a fight between two boxers in the ring.

        Returns:
            str: Name of the winning boxer.

        Raises:
            ValueError: If fewer than two boxers are in the ring.
        """
        if len(self.ring) < 2:
            logger.error("Attempted to fight with fewer than two boxers.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        logger.info(f"Fight result: {winner.name} defeated {loser.name}")
        self.clear_ring()
        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring."""
        if self.ring:
            logger.info("Clearing the ring.")
            self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add.

        Raises:
            TypeError: If the input is not a Boxer.
            ValueError: If ring already has two boxers.
        """
        if not isinstance(boxer, Boxer):
            logger.error("Attempted to enter non-Boxer object into ring.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Attempted to add boxer to full ring.")
            raise ValueError("Ring is full, cannot add more boxers.")

        logger.info(f"{boxer.name} has entered the ring.")
        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The two boxers in the ring.
        """
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on attributes.

        Args:
            boxer (Boxer): The boxer.

        Returns:
            float: Calculated fighting skill.
        """
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for {boxer.name}: {skill}")
        return skill