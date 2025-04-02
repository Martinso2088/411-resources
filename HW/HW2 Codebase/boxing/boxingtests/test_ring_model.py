import pytest
from boxing.models.boxers_model import Boxer
from boxing.ring_model import RingModel

@pytest.fixture
def boxer1():
    return Boxer(id=1, name="Rocky", weight=190, height=70, reach=72, age=28)

@pytest.fixture
def boxer2():
    return Boxer(id=2, name="Creed", weight=185, height=71, reach=73, age=30)

@patch("boxing.models.ring_model.update_boxer_stats")
@patch("boxing.models.ring_model.get_random", return_value=0.4)
def test_fight_success(mock_random, mock_update, boxer1, boxer2):
    ring = RingModel()
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    winner = ring.fight()
    assert winner in {boxer1.name, boxer2.name}
    assert len(ring.get_boxers()) == 0

def test_fight_too_few_boxers():
    ring = RingModel()
    with pytest.raises(ValueError):
        ring.fight()

def test_enter_ring_invalid_type():
    ring = RingModel()
    with pytest.raises(TypeError):
        ring.enter_ring("NotABoxer")

def test_enter_ring_full(boxer1, boxer2):
    ring = RingModel()
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    with pytest.raises(ValueError):
        ring.enter_ring(Boxer(id=3, name="Third", weight=170, height=68, reach=70, age=29))

