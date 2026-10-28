from __future__ import annotations

from anki_speech_trainer.review_state import ReviewSession, ReviewState


def test_card_change_invalidates_old_worker_session() -> None:
    session = ReviewSession()
    old_session = session.begin_card(10, mapped=True)
    session.recording()
    new_session = session.begin_card(11, mapped=True)

    assert old_session != new_session
    assert not session.accepts(old_session)
    assert session.accepts(new_session)
    assert session.state is ReviewState.IDLE


def test_unmapped_card_rejects_worker_messages() -> None:
    session = ReviewSession()
    session_id = session.begin_card(10, mapped=False)

    assert not session.accepts(session_id)


def test_state_records_worker_lifecycle_without_scheduler_effects() -> None:
    session = ReviewSession()
    session.begin_card(10, mapped=True)
    session.start_worker()
    session.worker_ready()
    session.recording()
    session.transcribing()
    session.result()

    assert session.state is ReviewState.RESULT
