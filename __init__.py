import logging
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

from .queries import get_outputs_sql, create_table_sql, add_record_sql
from .constants import (
    USERS_CONF,
    CARD_COUNT_CONF,
    TIME_BLOCK_SIZE_CONF,
    ENTITIES_BLACKLIST_CONF,
    DB_FILE,
    TABLE
)

DOMAIN = 'auto_ui'
DEPENDENCIES = []

USERS = {}
CARD_COUNT = 10
TIME_BLOCK_SIZE = 120
ENTITIES_BLACKLIST = []

_LOG = logging.getLogger(__name__)

card_placeholder = f'{DOMAIN}.placeholder'

conn = None

def setup(hass, config): # todo: use config values instead of const
    def init_outputs():
        hass.states.set(card_placeholder, "Placeholder, as the db fills you'll see this less")
        for user in USERS:
            for i in range(CARD_COUNT):
                _LOG.debug(f"Initiliazing component: {DOMAIN}.{USERS[user]}_{i}")
                hass.states.set(f"{DOMAIN}.{USERS[user]}_{i}", card_placeholder)
    
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

    def update_components(call):
        for user in USERS:
            cards = get_cards(user)
            i = 0
            for i in range(CARD_COUNT):
                try:
                    _LOG.info(f"Updating {DOMAIN}.{USERS[user]}_{i}={cards[i][0]}")
                    hass.states.set(f"{DOMAIN}.{USERS[user]}_{i}", cards[i][0])
                except IndexError:
                    # If the DB returned less entities than CARD_COUNT pad the rest with a placeholder card
                    hass.states.set(f"{DOMAIN}.{USERS[user]}_{i}", card_placeholder)


    def get_cards(user):
        start_time = datetime.utcnow() - timedelta(minutes = TIME_BLOCK_SIZE/2)
        end_time = datetime.utcnow() + timedelta(minutes = TIME_BLOCK_SIZE/2)

        _LOG.debug(f"Getting actions from " + start_time.strftime("%w %H:%M:%S utc") + " to " + end_time.strftime("%w %H:%M:%S utc"))
        
        c = conn.cursor()
        c.execute(
            get_outputs_sql(
                user, 
                start_time.strftime("%w %H:%M:%S"), 
                end_time.strftime("%w %H:%M:%S"),
                CARD_COUNT,
                ENTITIES_BLACKLIST
            )
        )
    
        return c.fetchall()

    # Listener to handle fired events
    def store_user_action(event):
        if event.context.user_id is None:
            _LOG.debug("Not saving action, user_id null")
            return

        if "entity_id" not in event.data["service_data"]:
            _LOG.debug("Not saving action, no entity id")
            return

        if isinstance(event.data["service_data"]["entity_id"], list):
            _LOG.debug("Not saving action, entity_id lists not supported")
            return
        
        if (event.context.user_id in USERS):
            _LOG.info(f"Storing user's ({USERS[event.context.user_id]}) action {event.data['service_data']['entity_id']} at {event.time_fired}")
            entry = (event.context.id, event.context.user_id, event.data["service_data"]["entity_id"], event.time_fired)

            c = conn.cursor()
            c.execute(add_record_sql(), entry)
            conn.commit()

    conf = config[DOMAIN]

    if USERS_CONF in conf:
        _LOG.debug(f"Users provided: {conf[USERS_CONF]}")
        global USERS
        USERS = conf[USERS_CONF]
    else:
        _LOG.error("users config entry is required")
        return false

    if CARD_COUNT_CONF in conf:
        _LOG.debug(f"Custom card count: {conf[CARD_COUNT_CONF]}")
        global CARD_COUNT
        CARD_COUNT = conf[CARD_COUNT_CONF]
    
    if TIME_BLOCK_SIZE_CONF in conf:
        _LOG.debug(f"Custom time block: {conf[TIME_BLOCK_SIZE_CONF]}")
        global TIME_BLOCK_SIZE
        TIME_BLOCK_SIZE = conf[TIME_BLOCK_SIZE_CONF]

    if ENTITIES_BLACKLIST_CONF in conf:
        _LOG.debug(f"Entities blacklist provided: {conf[ENTITIES_BLACKLIST_CONF]}")
        global ENTITIES_BLACKLIST
        ENTITIES_BLACKLIST = conf[ENTITIES_BLACKLIST_CONF]

    if not setup_db():
        return False

    init_outputs()
    update_components(None)

    # Register services
    hass.services.register(DOMAIN, 'update_outputs', update_components)

    # Store each call_service event
    hass.bus.listen("call_service", store_user_action)

    # Subscribe to updates every TIME_BLOCK_SIZE minutes
    hass.helpers.event.async_track_time_interval(
        update_components, 
        timedelta(minutes=TIME_BLOCK_SIZE/4)
    )
    
    # Return boolean to indicate that initialization was successful.
    return True

