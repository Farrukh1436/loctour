"""Finite-state machine definitions for registration flow."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()
    waiting_for_extra_info = State()
    waiting_for_payment_proof = State()
