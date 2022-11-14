import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

from example_sevents import events
from queries import get_outputs_sql, create_table_sql, add_record_sql
from constants import *

DOMAIN = 'auto_ui'
DEPENDENCIES = []

users = {
    'aecaac0f0f374df0be28f4918da681c1' : 'joel',
    '67b4acb998374d4d807430d4e2daac42' : 'kat'
} # todo: read users automatically

card_placeholder = 'sensor.current_hass_version_2' # todo: use component that shows as blank

conn = None

def setup(hass, config): # todo: use config
    def init_outputs:
        for user in users:
            for i in range(CARD_COUNT):
                hass.states.set(f"{DOMAIN}.{users[user]}_{i}", card_placeholder)

    def update_components(call):
        for user in users:
            cards = get_cards(user)
            i = 0
            for card in cards:
                hass.states.set(f"{DOMAIN}.{users[user]}_{i}", card[0])
                i += 1
    
    def setup_db():
        try:
            # Create connection
            global conn 
            conn = sqlite3.connect(DB_FILE)
            if conn is None:
                return False
            
            # Create table
            c = conn.cursor()
            c.execute(create_table_sql())
        except Error as e:
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
        if event.context.user_id is not None and event.context.user_id in users and event.data.service_data.entity_id is not None:
            # try:
            entry = (event.context.id, event.context.user_id, event.data.service_data.entity_id, event.time_fired)
            # except 

            c = conn.cursor()
            c.execute(add_record_sql(), entry)
            conn.commit()

    setup_db()
    update_components(void)

    # Store each call_service event
    hass.bus.listen("call_service", store_user_action)

    # Subscribe to updates every TIME_BLOCK_SIZE minutes
    hass.helpers.event.async_track_time_interval(
        update_components, 
        datetime.timedelta(minutes=TIME_BLOCK_SIZE)
    )
    
    # Return boolean to indicate that initialization was successful.
    return True

