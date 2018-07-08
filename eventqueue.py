from events import SayEvent, ChooseEvent, DamageEvent, StatusEvent
import typing

state = 0
queue = []
    
def activate_callback(callback, data=None):
    if callable(callback):
        callback = callback(data)
    if isinstance(callback, typing.Generator):
        try:
            func = next(callback)
            add_events(func(callback))
        except StopIteration:
            pass

def execute_events(scenes):
    for e in queue:
        if type(e) is SayEvent:
            scenes['dialogue'].handle_event(e)
        elif type(e) is ChooseEvent:
            # Open the selection text box with the options from data.
            scenes['choice'].handle_event(e)
        elif type(e) is DamageEvent:
            scenes['battle'].handle_event(e)
            activate_callback(e.callback)
        elif type(e) is StatusEvent:
            e.defending.status = e.status
            activate_callback(e.callback)
        else:
            raise ValueError(f'Event {e} is not recognized!')
    queue.clear()

def add_events(*events):
    global state
    for event in events:
        state += 1
        event.id = state
        queue.append(event)

def add_generator(generator):
    func = next(generator)
    add_events(func(generator))