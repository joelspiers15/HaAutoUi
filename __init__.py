import sqlite3

DOMAIN = 'auto_ui'

DEPENDENCIES = []

# High level variables
CARD_COUNT = 10
TIME_BLOCK_SIZE = 30
BLACKLISTED_ENTITIES = []

# SQL connection
database_file = '../../home-assistant_v2.db'
table = 'user_actions'

# SQL queries
sql_create_table = """ CREATE TABLE IF NOT EXISTS user_actions (
                                            id integer PRIMARY KEY,
                                            user_id text NOT NULL,
                                            entity_id text NOT NULL,
                                            time_fired text NOT NULL,
                                            day_of_week integer NOT NULL,
                                        ); """

users = {
    'aecaac0f0f374df0be28f4918da681c1' : 'joel',
    'abcdefg' : 'kat'
} # todo: replace with actual users
card_placeholder = 'card' # Will need an actual object
conn = None

def setup(hass, config):
    update_components(void)
    setup_db()


    def update_components(call):
        for user in users:
            cards = get_cards(user)
            for card in cards:
                hass.states.set('auto_ui.' + users[user] + '_' + i, card)
    
    def setup_db():
        try:
            # Create connection
            conn = sqlite3.connect(database_file)
            if conn is None:
                return False
            
            # Create table
            c = conn.cursor()
            c.execute(sql_create_table)
        except Error as e:
            print(e)
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
        return ['one', 'two', 'three']

    # Listener to handle fired events
    def store_user_action(event):
        sql = '''INSERT INTO user_actions(id,user_id,entity_id,time_fired,day_of_week) VALUES(?,?,?,?,?)'''
        # Only store user performed actions with entity ids
        if event.context.user_id is not None and event.context.user_id in users and event.data.service_data.entity_id is not None:
            entry = (event.context.id, event.context.user_id, event.data.service_data.entity_id, event.time_fired, 2) # todo: figure out actual day of the week

            c = conn.cursor()
            c.execute(sql, entry)
            conn.commit()

    # Store each call_service event
    hass.bus.listen("call_service", store_user_action)

    # Subscribe to updates every TIME_BLOCK_SIZE minutes
    hass.helpers.event.async_track_time_interval(
        update_components, 
        datetime.timedelta(minutes=TIME_BLOCK_SIZE)
    )
    
    # Return boolean to indicate that initialization was successful.
    return True

