"""
Definition of TaskProcessor Contract.

Take a look at these implementation of TaskProcessor for better understanding.
1. taskon.NaiveTaskProcessor
2. taskon.FiniteThreadTaskProcessor
3. taskon.InfiniteThreadTaskProcessor
4. taskon.RemoteExecutionTaskProcessor
"""

from taskon.abstract_task import AbstractTask
from taskon.common import taskonAssert

class AbstractTaskProcessor:
    """
    An abstract task processor. All the task processor implementations are
    derived from this class.
    All the task processor must comply the contract defined here.

    All 3 APIs (process, onComplete, close) will be called from a single
    threaded task scheduler. The implementation of these APIs can choose
    to be thread unsafe.
    """
    def process(self, task, on_complete_callback, *args, **kwargs):
        """
        This API should handle the request for the execution of the given @task
        as soon as possible and call the @on_complete_callback when the
        execution is complete.

        Task scheduler calls this API only when all the dependent
        tasks are complete. Hence task processor can execute the @task as soon
        as possible based on the availability of compute resources.
        The @args and @kwargs params given to this method are the
        actual inputs for this task after replacing `TaskResult(...)`
        placeholder with actual result of dependency task.

        If the @task return some output, it should be set via
        `@task.setResult(result)` API. If the task execution fails for some
        reason, the error should be set via `@task.setError(error)` API.
        The setResult/setError APIs can be called multiple times if required.
        setError API can be called with any object that has details of the
        error. Note that same error object will be returned by
        `task_runner.getTask(task_name).getError()`.

        This API should not raise exceptions. Task scheduler will abort if this
        API raise exception.
        The exceptions coming from the execution of @task should be catched
        internally and the error details should be set via @task.setError API.
        Usually stack trace (along with other details) are reported
        using @task.setError API. Look at 'taskon/naive_task_processor.py'

        When execution is complete and result/error is set using
        setResult/setError API, 'on_complete_callback' must be called exactly
        once with following parameters: (@task, status).
        status should be either taskon.TaskStatus.SUCCESS or
        taskon.TaskStatus.FAILURE. The 'on_complete_callback' should always be
        called irrespective of the success/failure status of the task execution.

        CAUTION: Note that the mandate on the callback is very strict. Other
        tasks which are dependent on this @task will never be executed
        otherwise. In that case task scheduler will keep waiting forever.

        Thread safety: The implementation of this method is free to be
        thread unsafe because this method will always be called from a single
        thread (task scheduler's main thread).
        Note: task scheduler doesn't have multiple threads.

        Ideally this API should not be blocking. i.e. this method should
        return instantly. Note that after calling this method, task scheduler
        will remain blocked until this method returns. As mentioned above,  
        The task scheduler, 'process' API, and all other API of this task
        processor will always run a single thread. Ideally this API should
        execute the given @task in a separate thread and return immediately.

        @on_complete_callback is thread safe to be used by child threads / any
        other thread.

        @task.setError / @task.setResult APIs are not thread safe but the task
        scheduler calls 'process' API (this API) exactly once for one task and
        the task schedular doesn't access @task object after 'process' API is
        called till @on_complete_callback is not called. Hence this
        method have the exclusive access to the @task object. Hence
        setError/setResult APIs are safe.
        """
        assert isinstance(task, AbstractTask)
        taskonAssert(False, "Purely abstract method 'process' should not "
                            "be called.")

    def onComplete(self, task):
        """
        Task scheduler calls onComplete API to acknowledge that task scheduler
        have received the information that execution of @task is complete.

        @task.getStatus() can be used to query the SUCCESS/FAILURE status of
        the @task.

        Thread safetly: The handler of this method is free to be thread unsafe
        because this method will always be called from a single thread - that
        is the main thread of task scheduler, which is the same thread from
        which 'process' API was called.

        Hence a TaskProcessor implementation can maintain a state access by
        process and onComplete methods in a thread unsafe way, because these
        two method will always remain exclusive because of single threaded
        task scheduler.
        """
        assert isinstance(task, AbstractTask)

    def close(self):
        """
        Task scheduler calls close API to guarantee that task scheduler
        won't schedule more tasks. task processor implementers can use this
        handler to close their internal resources.

        Thread safetly: The handler of this method is free to be thread unsafe
        because this method will always be called a single thread - that is the
        main thread of task scheduler.

        Note that: If the task processor is desired to be used in reusable way,
        i.e. we want to reuse the same task processor in multiple
        scheduler, the 'process' API should be functional even after
        close API is called. Implementation can reallocate the
        resources in the handler of 'process' API if the resources
        are closed. Take a look at taskon/finite_thread_task_processor.py.
        """
        pass

