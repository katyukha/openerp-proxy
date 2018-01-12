"""This module contains some IPython integration utils
"""


def in_progress(seq, msg="Progress: [%(processed)d / %(total)d]", length=None, close=True):
    """ Iterate over sequence, yielding item with progress widget displayed.
        This is useful if you need to precess sequence of items with some
        time consuming operations

        .. note::

            This works only in Jupyter Notebook

        .. note::

            This function requires *ipywidgets* package to be installed

        :param seq: sequence to iterate on.
        :param str msg: (optional) message template to display.
                        Following variables could be used in this template:
                            - processed
                            - total
                            - time_total
                            - time_per_item
        :param int length: (optional) if seq is generator, or it is not
                           possible to apply 'len(seq)' function to 'seq',
                           then this argument is required and it's value will
                           be used as total number of items in seq.

        Example example::

            import time
            for i in in_progress(range(10)):
                time.sleep(1)
    """
    from IPython.display import display
    from ipywidgets import IntProgress
    import time

    if length is None:
        length = len(seq)

    start_time = time.time()

    progress = IntProgress(value=0, min=0, max=length,
                           description=msg % {'processed': 0,
                                              'total': length,
                                              'time_total': 0.0,
                                              'time_per_item': 0.0,
                                              'time_remaining': 0.0,})
    display(progress)

    for i, item in enumerate(seq, 1):
        progress.value = i

        i_start_time = time.time()

        yield item  # Do the job

        i_end_time = time.time()

        progress.description = msg % {
            'processed': i,
            'total': length,
            'time_total': i_end_time - start_time,
            'time_per_item': (i_end_time - start_time) / i,
            'time_remaining': ((i_end_time - start_time) / i) * (length - i),
        }

    if close:
        progress.close()
