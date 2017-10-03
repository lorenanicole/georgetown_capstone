# Example Scripts

Each example script has a docstring at the top of the file explaining the purpose of each. Included in this repo we have:
- `create_db.py`: Script demonstrating how to use boto3 to create a database on AWS
- `query.py`: Example of a Python class `Query`, that uses `psycopg2` to get data with retry logic, and `PandasQuery` that will use Pandas to execute a SQL query and return a Pandas dataframe.
- `s3.py`: Example of how to upload to an already existing S3 bucket and downloading from an S3 bucket to a Pandas dataframe.
- `seed_database.py`: Example of checking if a table exists, if not creates a table on the AWS database, then inserts data into the table by loading TSV from local filesystem using a `Query` class.
- `useful_queries.py`: One way of how to bundle queries in a Python script to be imported across files.
- `wikipedia_talk_corpus`: Uses BeautifulSoup to locate a URL to try to download data.

All of these scripts make use of Python3.6 and require installation of Python dependencies in the `../requirements.txt` file. You'll need to create a `config.yml` that mirrors the `example-config.yml` for scripts to work.