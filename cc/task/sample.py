"""Sample task.

Params:
    cmd - crash-launch / crash-run / other
"""

import sys
import time

import skytools

from cc.task import CCTask

class SampleTask(CCTask):

    log = skytools.getLogger('cc.task.sample')

    def fetch_config(self):

        # crash before daemonizing if requested
        t = self.task_info['task']
        if t['cmd'] == 'crash-launch':
            raise Exception('launch failed')

        return CCTask.fetch_config(self)

    def process_task(self, task):

        # crash during run
        if task['cmd'] == 'crash-run':
            raise Exception('run failed')

        # do some work
        for i in range(3):
            time.sleep(1)
            fb = {'i': i}
            self.send_feedback (fb)
        # task done
        self.log.info ('task %s done', task['task_id'])
        self.send_finished()

if __name__ == '__main__':
    t = SampleTask('cc.task.sample', sys.argv[1:])
    t.start()
