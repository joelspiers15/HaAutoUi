DOMAIN = 'auto_ui'

DEPENDENCIES = []

CARD_COUNT = 10
TIME_BLOCK_SIZE = 30
BLACKLISTED_ENTITIES = []

users = ['joel', 'kat'] # todo: replace with actual users
card_placeholder = 'card' # Will probably need an actual object

def setup(hass, config):
    update_components(void)

    def update_components(call):
        for user in users:
            cards = get_cards(user)
            for card in cards:
                hass.states.set('auto_ui.' + user + '_' + i, card)
    
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
        # Only store user performed actions with entity ids
        if event.context.user_id is not None and event.data.service_data.entity_id is not None:
            print("store here")

    # Store each call_service event
    hass.bus.listen("call_service", store_user_action)

    # Subscribe to updates every TIME_BLOCK_SIZE minutes
    hass.helpers.event.async_track_time_interval(
        update_components, 
        datetime.timedelta(minutes=TIME_BLOCK_SIZE)
    )
    
    # Return boolean to indicate that initialization was successful.
    return True

