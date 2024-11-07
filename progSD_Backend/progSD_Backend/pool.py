import psycopg2
from psycopg2 import pool
from django.db.backends.postgresql.base import DatabaseWrapper as Psycopg2DatabaseWrapper

class DatabaseWrapper(Psycopg2DatabaseWrapper):
    def get_new_connection(self, conn_params):
        if not hasattr(self, '_pool'):
            # Create a connection pool (adjust min and max connections as needed)
            self._pool = psycopg2.pool.SimpleConnectionPool(1, 10, **conn_params)
        # Get a connection from the pool
        return self._pool.getconn()

    def close(self):
        # Override the close method to release the connection back to the pool
        if hasattr(self, '_pool'):
            self._pool.putconn(self.connection)
        else:
            super().close()
