import pytest
from app.crud.crud_journey import (
    create_journey,
    get_journey,
    get_journeys_by_user,
    get_equivalent_journey,
    clone_journey_for_user
)
from app.schemas.journey import JourneyCreate
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.models.user import User

@pytest.fixture
def dummy_user(db):
    """Creates a dummy user for journey ownership."""
    user = User(email="cruduser@larry.ai", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def dummy_user_two(db):
    user = User(email="cruduser2@larry.ai", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_create_and_get_journey(db, dummy_user):
    journey_in = JourneyCreate(
        user_id=dummy_user.id,
        original_prompt="I want to learn Python",
        target_days=3,
        journey_title="Python 101",
        overview="Intro to python",
        prompt_embedding=[0.1, 0.2, 0.3]
    )
    created = create_journey(db, journey_in)
    
    assert created.id is not None
    assert created.user_id == dummy_user.id
    
    fetched = get_journey(db, created.id)
    assert fetched is not None
    assert fetched.journey_title == "Python 101"
    
    user_journeys = get_journeys_by_user(db, dummy_user.id)
    assert len(user_journeys) == 1
    assert user_journeys[0].id == created.id

def test_get_equivalent_journey(db, dummy_user):
    journey_in = JourneyCreate(
        user_id=dummy_user.id,
        original_prompt=" Learn C++ ",
        target_days=5,
        journey_title="C++ Mastery",
        overview="Learn C++"
    )
    create_journey(db, journey_in)
    
    # Exact match after trimming and lowercasing
    match_1 = get_equivalent_journey(db, "learn c++", 5)
    assert match_1 is not None
    assert match_1.journey_title == "C++ Mastery"
    
    # Case insensitivity and whitespace check
    match_2 = get_equivalent_journey(db, "   LEARN C++  ", 5)
    assert match_2 is not None
    
    # Wrong days should miss
    miss_1 = get_equivalent_journey(db, "learn c++", 3)
    assert miss_1 is None
    
    # Wrong prompt should miss
    miss_2 = get_equivalent_journey(db, "learn python", 5)
    assert miss_2 is None

def test_clone_journey_for_user(db, dummy_user, dummy_user_two):
    # 1. Create a template journey for user 1 with daily plans
    template = Journey(
        user_id=dummy_user.id,
        original_prompt="Machine Learning",
        target_days=2,
        journey_title="ML Basics",
        overview="Intro to ML"
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    plan1 = DailyPlan(journey_id=template.id, day_number=1, title="Day 1", concepts_to_cover=["A"], difficulty="Beginner", completion_status=True)
    plan2 = DailyPlan(journey_id=template.id, day_number=2, title="Day 2", concepts_to_cover=["B"], difficulty="Beginner", completion_status=True)
    db.add_all([plan1, plan2])
    db.commit()
    
    # Refresh to load daily plans
    template = get_equivalent_journey(db, "Machine Learning", 2)
    
    # 2. Clone it for user 2
    cloned = clone_journey_for_user(db, template, dummy_user_two.id)
    
    assert cloned.id != template.id
    assert cloned.user_id == dummy_user_two.id
    assert cloned.journey_title == "ML Basics"
    
    # 3. Verify plans were cloned and completion_status was reset
    db.refresh(cloned)
    assert len(cloned.daily_plans) == 2
    for plan in cloned.daily_plans:
        assert plan.journey_id == cloned.id
        assert plan.completion_status is False  # Must be reset!

    # 4. Cloning again should return the exact same cloned journey (idempotency check)
    cloned_again = clone_journey_for_user(db, template, dummy_user_two.id)
    assert cloned_again.id == cloned.id
