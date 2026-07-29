"""Estados conversacionales que no sustituyen el estado persistente del pedido."""

from aiogram.fsm.state import State, StatesGroup


class ClientOrderStates(StatesGroup):
    """Pasos temporales necesarios para interpretar la próxima entrada."""

    waiting_quantity = State()
