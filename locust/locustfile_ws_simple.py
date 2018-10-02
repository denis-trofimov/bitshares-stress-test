#I was playing around with this today and also found the custom example a little tricky, because it's hard to tell where the magic happens. Here's a much simpler version of a client and task and user interaction. Instead of the decorator that catches any arbitrary method to the client, I made it only able to do one thing so you can see where the timing and error handling happen, and how it uses the locust event hooks to send successes and failures.
#and then you could run this in your terminal with something like:
#locust - f simple_test.py - - no-web - - clients = 2 - - hatch-rate = 2 - - num-request = 4 - - print-stats - - only-summary

import time

from locust import TaskSet, task, Locust, events


class SimpleClient(object):

    def __init__(self):
        pass

    def execute(self, name):
        start_time = time.time()
        try:
            print("do your things cause stress and throw exceptions here.")
            time.sleep(1)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="execute", name=name, response_time=total_time, exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="execute", name=name, response_time=total_time, response_length=0)


class SimpleTasks(TaskSet):

    @task
    def simple_task(self):
        self.client.execute('simple_things')


class SimpleUser(Locust):
    def __init__(self, *args, **kwargs):
        super(Locust, self).__init__(*args, **kwargs)
        self.client = SimpleClient()

    task_set = SimpleTasks
    min_wait = 1000
    max_wait = 10000
