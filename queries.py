import logging

from .constants import (
    CARD_COUNT,
    TIME_BLOCK_SIZE,
    BLACKLISTED_ENTITIES,
    DB_FILE,
    TABLE
)

_LOG = logging.getLogger(__name__)

def get_outputs_sql(user_id, start_time, end_time):
    q = f"""
        SELECT entity_id, COUNT(DISTINCT id) as count

        FROM {TABLE} 

        WHERE strftime('%w %H:%M:%S', time_fired) >= '{start_time}' 
        AND strftime('%w %H:%M:%S', time_fired) < '{end_time}' 
        AND user_id = '{user_id}' 

        GROUP BY entity_id
        ORDER BY count DESC
        LIMIT {CARD_COUNT};
    """
    _LOG.debug(f"q = {q}")
    return q

def create_table_sql():
    q = f""" 
        CREATE TABLE IF NOT EXISTS {TABLE} (
            id text PRIMARY KEY,
            user_id text NOT NULL,
            entity_id text NOT NULL,
            time_fired datetime NOT NULL
        ); 
    """
    _LOG.debug(f"q = {q}")
    return q

def add_record_sql():
    q = f"""
        INSERT INTO 
        {TABLE}(id,user_id,entity_id,time_fired) 
        VALUES(?,?,?,?);
    """
    _LOG.debug(f"q = {q}")
    return q

