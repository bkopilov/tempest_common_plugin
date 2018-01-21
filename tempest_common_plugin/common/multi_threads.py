
from queue import Queue

import threading
import random


class ThreadManager(object):

    def __init__(self, callback, number_of_threads, infinite_loop=False,
                 kwargs_list=None):
        """

        :param callback: Reference to function to run in a thread
        :param kwargs_list: list of dictionaries, each one trigger a thread
        :param number_of_threads: When this option not none, kward can be :
        empty - callback without params
        with kwargs - same kwargs[0] to all callback

        The idea here to get a callback function and run it in parallel when
        kwargs of dictionaries or same kwargs to all threads

        """
        self.callback = callback
        self.number_of_threads = number_of_threads
        self.kwargs_list = kwargs_list
        self.infinite_loop = infinite_loop
        self.threads_output = list()
        self.instance_threads = list()
        self._shared_queue = Queue()

    def _start_thread(self, callback, kwargs_list=None):
        """
        :param callback:
        :param kwargs_list:
        :return:
        """
        if kwargs_list:
            thread = MyThread(callback, self._shared_queue, self.infinite_loop,
                              kwargs_list)
        else:
            thread = MyThread(callback, self._shared_queue, self.infinite_loop)
        self.instance_threads.append(thread)
        thread.start()

    def start(self):
        workers = self.number_of_threads
        # starting threads
        start_index = 0
        while start_index < workers:
            if self.kwargs_list:
                self._start_thread(self.callback,
                                   kwargs_list=self.kwargs_list[start_index])
            else:
                self._start_thread(self.callback)
            start_index += 1

    def join_threads(self):
        # when the threads terminated , main caller is waiting
        # we get all data from threads.
        for thread in self.instance_threads:
            thread.join()

    def force_join_threads(self):
        for thread in self.instance_threads:
            thread.set_infinite_loop(False)
            thread.join()

    def get_output(self, filter_by=None):
        if filter_by:
            return [output[filter_by] for output in self._shared_queue.queue]
        return self._shared_queue.queue


class MyThread(threading.Thread):
    def __init__(self, callback, shared_queue, infinite_loop=False,
                 kwargs=None):
        """
        :param callback:  a single thread with a callback
        :param kwargs_list: a dictionary of params
        """
        randbits = str(random.randint(1, 0x7fffffff))
        super(MyThread, self).__init__(name="test_" + randbits)
        self.output = None
        self.callback = callback
        self.shared_queue = shared_queue
        self.kwargs = kwargs
        self._infinite_loop = infinite_loop

    def run(self):
        while True:
            try:
                if self.kwargs:
                    output_info = self.callback(**self.kwargs)
                    self.shared_queue.put(output_info)
                else:
                    output_info = self.callback()
                    self.shared_queue.put(output_info)
                if not self._infinite_loop:
                    break

            except Exception as e:
                raise RuntimeError(
                    str("callback: %s kwargs: %s Exception: %s " % (
                        self.callback, self.kwargs, str(e.message))))

    def set_infinite_loop(self, boolean):
        self._infinite_loop = boolean
