"""
Example script using boto3 to create a new RDS postgres instance on AWS.
Uses secrets for a secure password.
"""


import time
import boto3
import botocore
import secrets
import string

def create_password(length=20):
    '''
    Creates a unique password using the Python secrets library of length n

    :param int length: length of password
    :return: str unique 20 char password
    '''

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def main(db_identifier, db_name, user_name):
    '''
    Sample code to create an AWS RDS Postgres database.
    AWS documentation available at: https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_CreateDBInstance.html
    '''

    session = boto3.session.Session(profile_name=user_name)
    # List of regions http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
    rds = session.client('rds', 'us-east-1')
    password = create_password()
    print('Password is: {0}'.format(password))

    try:
        rds.create_db_instance(DBInstanceIdentifier=db_identifier,
                               AllocatedStorage=20,
                               DBName=db_name,
                               Engine='postgres',
                               # General purpose SSD
                               StorageType='gp2',
                               StorageEncrypted=False,
                               AutoMinorVersionUpgrade=True,
                               # Set this to true later?
                               MultiAZ=False,
                               MasterUsername='group_admin',
                               MasterUserPassword=password,
                               DBInstanceClass='db.t2.micro')
        print('Starting RDS instance with ID: {0}'.format(db_identifier))
    except botocore.exceptions.ClientError as e:
        if 'DBInstanceAlreadyExists' in e.message:
            print('DB instance {0} exists already, continuing to poll ...'.format(db_identifier))
        else:
            raise


    running = True
    while running:
        response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)

        db_instances = response['DBInstances']
        if len(db_instances) != 1:
            raise Exception('Whoa cowboy! More than one DB instance returned; this should never happen')

        db_instance = db_instances[0]

        status = db_instance['DBInstanceStatus']

        print('Last DB status: {0}'.format(status))

        time.sleep(5)
        if status == 'available':
            endpoint = db_instance['Endpoint']
            host = endpoint['Address']
            # port = endpoint['Port']

            print('DB instance ready with host: {0}'.format(host))
            running = False


if __name__ == '__main__':
    db_identifier = 'cyberbullying'
    db_name = 'cyberbullying'
    user_name = 'lmesa'
    main(db_identifier, db_name, user_name)

    # describe_db_instances() will return list of all instances