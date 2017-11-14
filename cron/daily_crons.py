import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from crontab import CronTab

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CRON_LIST = [

]
def main():
    users_cron = CronTab(user='group_admin')

    job = users_cron.new(command='cd {0}/{1}; python3 '.format(BASE_DIR, 'customer_details'))
    job.setall('00 08 * * *')
    job.enable()

    users_cron.write()
    print(users_cron.render())

if __name__ == "__main__":
  main()