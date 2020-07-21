"""
Definition of TaskProcessor Contract.

Take a look at these implementation of TaskProcessor for better understanding.
1. taskon.NaiveTaskProcessor
2. taskon.SingleThreadTaskProcessor
3. taskon.MultiThreadTaskProcessor
4. taskon.RemoteExecutionTaskProcessor
"""

from taskon.abstract_task import AbstractTask


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
        Handle the request for the execution of the given @task as soon as
        possible and call the @on_complete_callback when the execution is
        complete.

        Task scheduler calls this API only when all the dependent
        tasks are complete. @args and @kwargs given to this method are the
        actual inputs for this task after replacing `TaskResult(...)`
        placeholder with actual result of dependency task.

        If the task return some output, it should be set via
        `@task.setResult(result)` API. If the task execution fails for some
        reason, the error should be set via `@task.setError(error)` API.
        setResult or setError API should be called. setResult/setError APIs
        can be called multiple times if required.
        setError API can be called with any object that has details of the
        error. Note that same error object will be returned by
        `task_runner.error("task_name")` at the end.

        This API should not raise exceptions. Task scheduler will abort if this
        API raise exception.
        The exceptions coming from the execution of @task should be catched.
        Ideally stack trace (along with other details) should be reported by
        updated using @task.setError API.

        When execution is complete and setResult/setError is called,
        'on_complete_callback' must be called exactly once with
        following parameters: (task, status).
        The 'on_complete_callback' should always be called irrespective of the
        success/failure status of the task execution.
        status must be either taskon.TaskStatus.SUCCESS or
        taskon.TaskStatus.FAILURE

        CAUTION: Note that the mandate on the callback is very strict. Other
        tasks which are dependent on this @task will never be executed
        otherwise and the task scheduler will keep waiting forever if
        timeout is not set for the given @task.

        Thread safety: The implementation of this method is free to be
        thread unsafe because this method will always be called from a single
        thread - that is the main thread of task scheduler.
        Note: task scheduler doesn't have multiple threads.

        Ideally this API should not be blocking. i.e. this method should
        return instantly. Note that after calling this method, task scheduler
        will remain blocked until this method returns. (As mentioned above -
        task scheduler, 'process' API and the 'onComplete' API are always in a
        single thread). Ideally this API should execute the given @task in a
        separate thread.

        @on_complete_callback is thread safe to be used by child threads / any
        other thread.

        @task.setError / @task.setResult APIs are not thread safe but the task
        scheduler calls 'process' API (this API) exactly once for one task and
        the task schedular doesn't access @task object after 'process' API is
        called till the time @on_complete_callback is not called. Hence this
        method have the exclusive access to the @task object. Hence
        setError/setResult APIs are safe.
        """
        assert isinstance(task, AbstractTask)

    def onComplete(self, task):
        """
        Task scheduler calls onComplete API to acknowledge that task scheduler
        have received the information that execution of @task is complete.

        task.getStatus() can be used to query the execution status of the task.

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
        """
        pass