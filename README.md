# Georgetown Capstone Project: Cyberbullying

A repository for the Georgetown School of Continuing Studies Data Science Certificate capstone. Project is to identify instances of cyberbullying.

### Project Structure

Project structure contains the following modules:
- `analysis`: Python code + Jupyter notebooks for analysis
- `cron`: Python code to setup various cronjobs e.g. daily Reddit scraper
- `data`: Example data sets for local storage (temporary; should be used for exploratory purposes; upload to AWS instead)
- `examples`: Example scripts for working with AWS RDS database + S3, Pandas, writing class wrapper for `psycopg2`
- `papers`: Papers collected that investigates the cyberbullying problem space


### Daily Crons

This project was setup using the free tier of AWS. The EC2 instance is an Amazon instance, has Python 3.4 installed, and
requires a Python 3.4 virtualenv for the daily cron to run as is. The cronjobs are ran as the default `ec2-user`. 

Example for how to setup cron jobs:
1. `ssh -i path/to/key.pem ec2-user@public-ec2-domain`
2. Logic to activate Python 3.4 virtualenv
3. `python cron/daily_crons.py`
4. You can view cronjobs via `crontab -e`

### Getting Started

To get started you'll need to:
- Setup a Python 3.4 `virtualenv` (by convention named `venv` as that's what's ignored in `.gitignore`) using the `requirements.txt` file, else use `conda`
- Note: If using AWS EC2 Amazon image, you may need to confirm the proper pip is used to install depedendencies. You don't want system pip but the virtualenv pip `/venv/local/bin/pip3.4`.
- Create a `config.yml` using your credentials, use `example-config.yml` as a template
- Setup AWS credentials via `aws configure`

### Questions?

Contact Lorena Mesa via email (me@lorenamesa.com) or [http://twitter.com/loooorenanicole](Twitter).

Thanks folks! 