import logging
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

from .queries import get_outputs_sql, create_table_sql, add_record_sql
from .constants import (
    CARD_COUNT,
    TIME_BLOCK_SIZE,
    BLACKLISTED_ENTITIES,
    DB_FILE,
    TABLE
)

DOMAIN = 'auto_ui'
DEPENDENCIES = []

_LOG = logging.getLogger(__name__)

users = {
    'aecaac0f0f374df0be28f4918da681c1' : 'joel',
    '67b4acb998374d4d807430d4e2daac42' : 'kat'
} # todo: read users automatically

card_placeholder = 'sensor.current_hass_version_2' # todo: use component that shows as blank

conn = None

def setup(hass, config): # todo: use config values instead of const
    def init_outputs():
        for user in users:
            for i in range(CARD_COUNT):
                _LOG.debug(f"Initiliazing component: {DOMAIN}.{users[user]}_{i}")
                hass.states.set(f"{DOMAIN}.{users[user]}_{i}", card_placeholder)

    def update_components(call):
        for user in users:
            cards = get_cards(user)
            i = 0
            for card in cards:
                _LOG.debug(f"Updating {DOMAIN}.{users[user]}_{i}={card[0]}")
                hass.states.set(f"{DOMAIN}.{users[user]}_{i}", card[0])
                i += 1
    
    def setup_db():
        try:
            # Create connection
            global conn 
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            if conn is None:
                _LOG.error("Failed to open DB connection")
                return False

            # Create table
            c = conn.cursor()
            c.execute(create_table_sql())
        except Error as e:
            _LOG.error("Error while setting up DB", e)
            return False

    def get_cards(user):
        # Query list of cards for current time block and user
        #   user_id == user_id
        #   day_of_week == {current day of the week}
        #   time_fired >= now() - ( TIME_BLOCK_SIZE/2 )
        #   time_fired <= now() + ( TIME_BLOCK_SIZE/2 )
        #   combine matching entity ids with new `count` field
        #   sort by count
        #   select top CARD_COUNT

        start_time = datetime.now() - timedelta(minutes = TIME_BLOCK_SIZE/2)
        end_time = datetime.now() + timedelta(minutes = TIME_BLOCK_SIZE/2)
        
        c = conn.cursor()
        c.execute(
            get_outputs_sql(
                user, 
                start_time.strftime("%H:%M:%S"), 
                end_time.strftime("%H:%M:%S"), 
                datetime.now().strftime("%w")
            )
        )
    
        return c.fetchall()

    # Listener to handle fired events
    def store_user_action(event):
        # Only store user performed actions with entity ids
        if event.context.user_id is None:
            _LOG.debug("Not saving action, user_id null")
            return

        if "entity_id" not in event.data["service_data"]:
            _LOG.debug("Not saving action, no entity id")
            return
        
        if (event.context.user_id in users and event.data["service_data"]["entity_id"] not in BLACKLISTED_ENTITIES):
            _LOG.info(f"Storing user action {event.data['service_data']['entity_id']}")
            entry = (event.context.id, event.context.user_id, event.data["service_data"]["entity_id"], event.time_fired)

            c = conn.cursor()
            c.execute(add_record_sql(), entry)
            conn.commit()

    setup_db()
    init_outputs()
    update_components(None)

    hass.states.set(f"{DOMAIN}.joel_0", "input_boolean.asleep")
    hass.states.set(f"{DOMAIN}.joel_1", "script.fix_top_monitor")
    hass.states.set(f"{DOMAIN}.joel_2", "remote.harmony_hub")
    hass.states.set(f"{DOMAIN}.joel_3", "light.bedroom_light_1")
    hass.states.set(f"{DOMAIN}.joel_4", "script.bedroom_relax")

    # Store each call_service event
    hass.bus.listen("call_service", store_user_action)

    # Subscribe to updates every TIME_BLOCK_SIZE minutes
    hass.helpers.event.async_track_time_interval(
        update_components, 
        timedelta(minutes=TIME_BLOCK_SIZE)
    )
    
    # Return boolean to indicate that initialization was successful.
    return True

