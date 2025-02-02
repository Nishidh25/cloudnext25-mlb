"""Create SQLAlchemy engine and session objects."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import os

# creates SQLALCHEMY object
instance_connection_name = os.getenv('instance_connection_name','') # e.g. 'project:region:instance'
db_user = os.getenv('db_user','')
db_pass = os.getenv('db_pass','')
db_name = os.getenv('db_name','')
ip_type = IPTypes.PRIVATE

connector = Connector(
    ip_type="private",  # can also be "private" or "psc"
    enable_iam_auth=False,
    timeout=30,
    #credentials=custom_creds # google.auth.credentials.Credentials
)

def getconn() -> pg8000.dbapi.Connection:
    conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
    )
    return conn

# The Cloud SQL Python Connector can be used with SQLAlchemy
# using the 'creator' argument to 'create_engine'

# Create database engine
engine = create_engine("postgresql+pg8000://",creator=getconn)

# Create database session
Session = sessionmaker(bind=engine)
session = Session()