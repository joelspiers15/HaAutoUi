from .constants import (
    CARD_COUNT,
    TIME_BLOCK_SIZE,
    BLACKLISTED_ENTITIES,
    DB_FILE,
    TABLE
)

def get_outputs_sql(user_id, start_time, end_time, day_of_week):
    return f"""
        SELECT entity_id, COUNT(DISTINCT id) as count

        FROM {TABLE} 

        WHERE time(time_fired) >= '{start_time}' 
        AND time(time_fired) < '{end_time}' 
        AND CAST (strftime('%w', time_fired) AS Integer) = {day_of_week}
        AND user_id = '{user_id}' 

        GROUP BY entity_id
        ORDER BY count DESC
        LIMIT {CARD_COUNT};
    """

def create_table_sql():
    return f""" 
        CREATE TABLE IF NOT EXISTS {TABLE} (
            id text PRIMARY KEY,
            user_id text NOT NULL,
            entity_id text NOT NULL,
            time_fired datetime NOT NULL
        ); 
    """

def add_record_sql():
    return f"""
        INSERT INTO 
        {TABLE}(id,user_id,entity_id,time_fired) 
        VALUES(?,?,?,?)
    """

