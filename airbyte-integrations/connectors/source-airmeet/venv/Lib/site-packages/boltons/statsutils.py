# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""``statsutils`` provides tools aimed primarily at descriptive
statistics for data analysis, such as :func:`mean` (average),
:func:`median`, :func:`variance`, and many others,

The :class:`Stats` type provides all the main functionality of the
``statsutils`` module. A :class:`Stats` object wraps a given dataset,
providing all statistical measures as property attributes. These
attributes cache their results, which allows efficient computation of
multiple measures, as many measures rely on other measures. For
example, relative standard deviation (:attr:`Stats.rel_std_dev`)
relies on both the mean and standard deviation. The Stats object
caches those results so no rework is done.

The :class:`Stats` type's attributes have module-level counterparts for
convenience when the computation reuse advantages do not apply.

>>> stats = Stats(range(42))
>>> stats.mean
20.5
>>> mean(range(42))
20.5

Statistics is a large field, and ``statsutils`` is focused on a few
basic techniques that are useful in software. The following is a brief
introduction to those techniques. For a more in-depth introduction,
`Statistics for Software
<https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_,
an article I wrote on the topic. It introduces key terminology vital
to effective usage of statistics.

Statistical moments
-------------------

Python programmers are probably familiar with the concept of the
*mean* or *average*, which gives a rough quantitiative middle value by
which a sample can be can be generalized. However, the mean is just
the first of four `moment`_-based measures by which a sample or
distribution can be measured.

The four `Standardized moments`_ are:

  1. `Mean`_ - :func:`mean` - theoretical middle value
  2. `Variance`_ - :func:`variance` - width of value dispersion
  3. `Skewness`_ - :func:`skewness` - symmetry of distribution
  4. `Kurtosis`_ - :func:`kurtosis` - "peakiness" or "long-tailed"-ness

For more information check out `the Moment article on Wikipedia`_.

.. _moment: https://en.wikipedia.org/wiki/Moment_(mathematics)
.. _Standardized moments: https://en.wikipedia.org/wiki/Standardized_moment
.. _Mean: https://en.wikipedia.org/wiki/Mean
.. _Variance: https://en.wikipedia.org/wiki/Variance
.. _Skewness: https://en.wikipedia.org/wiki/Skewness
.. _Kurtosis: https://en.wikipedia.org/wiki/Kurtosis
.. _the Moment article on Wikipedia: https://en.wikipedia.org/wiki/Moment_(mathematics)

Keep in mind that while these moments can give a bit more insight into
the shape and distribution of data, they do not guarantee a complete
picture. Wildly different datasets can have the same values for all
four moments, so generalize wisely.

Robust statistics
-----------------

Moment-based statistics are notorious for being easily skewed by
outliers. The whole field of robust statistics aims to mitigate this
dilemma. ``statsutils`` also includes several robust statistical methods:

  * `Median`_ - The middle value of a sorted dataset
  * `Trimean`_ - Another robust measure of the data's central tendency
  * `Median Absolute Deviation`_ (MAD) - A robust measure of
    variability, a natural counterpart to :func:`variance`.
  * `Trimming`_ - Reducing a dataset to only the middle majority of
    data is a simple way of making other estimators more robust.

.. _Median: https://en.wikipedia.org/wiki/Median
.. _Trimean: https://en.wikipedia.org/wiki/Trimean
.. _Median Absolute Deviation: https://en.wikipedia.org/wiki/Median_absolute_deviation
.. _Trimming: https://en.wikipedia.org/wiki/Trimmed_estimator


Online and Offline Statistics
-----------------------------

Unrelated to computer networking, `online`_ statistics involve
calculating statistics in a `streaming`_ fashion, without all the data
being available. The :class:`Stats` type is meant for the more
traditional offline statistics when all the data is available. For
pure-Python online statistics accumulators, look at the `Lithoxyl`_
system instrumentation package.

.. _Online: https://en.wikipedia.org/wiki/Online_algorithm
.. _streaming: https://en.wikipedia.org/wiki/Streaming_algorithm
.. _Lithoxyl: https://github.com/mahmoud/lithoxyl

"""


import bisect
from math import floor, ceil
from collections import Counter


class _StatsProperty:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)


class Stats:
    """The ``Stats`` type is used to represent a group of unordered
    statistical datapoints for calculations such as mean, median, and
    variance.

    Args:

        data (list): List or other iterable containing numeric values.
        default (float): A value to be returned when a given
            statistical measure is not defined. 0.0 by default, but
            ``float('nan')`` is appropriate for stricter applications.
        use_copy (bool): By default Stats objects copy the initial
            data into a new list to avoid issues with
            modifications. Pass ``False`` to disable this behavior.
        is_sorted (bool): Presorted data can skip an extra sorting
            step for a little speed boost. Defaults to False.

    """
    def __init__(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def _get_sorted_data(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if not self._use_copy:
            return sorted(self.data)
        elif not self._is_sorted:
            self.data.sort()
        return self.data

    def clear_cache(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def _calc_count(self):
        """The number of items in this Stats object. Returns the same as
        :func:`len` on a Stats object, but provided for pandas terminology
        parallelism.

        >>> Stats(range(20)).count
        20
        """
        return len(self.data)
    count = _StatsProperty('count', _calc_count)

    def _calc_mean(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, 0.0) / len(self.data)
    mean = _StatsProperty('mean', _calc_mean)

    def _calc_max(self):
        """
        The maximum value present in the data.

        >>> Stats([2, 1, 3]).max
        3
        """
        if self._is_sorted:
            return self.data[-1]
        return max(self.data)
    max = _StatsProperty('max', _calc_max)

    def _calc_min(self):
        """
        The minimum value present in the data.

        >>> Stats([2, 1, 3]).min
        1
        """
        if self._is_sorted:
            return self.data[0]
        return min(self.data)
    min = _StatsProperty('min', _calc_min)

    def _calc_median(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), 0.5)
    median = _StatsProperty('median', _calc_median)

    def _calc_iqr(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(0.75) - self.get_quantile(0.25)
    iqr = _StatsProperty('iqr', _calc_iqr)

    def _calc_trimean(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0
    trimean = _StatsProperty('trimean', _calc_trimean)

    def _calc_variance(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        global mean  # defined elsewhere in this file
        return mean(self._get_pow_diffs(2))
    variance = _StatsProperty('variance', _calc_variance)

    def _calc_std_dev(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance ** 0.5
    std_dev = _StatsProperty('std_dev', _calc_std_dev)

    def _calc_median_abs_dev(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median([abs(x - v) for v in sorted_vals])
    median_abs_dev = _StatsProperty('median_abs_dev', _calc_median_abs_dev)
    mad = median_abs_dev  # convenience

    def _calc_rel_std_dev(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default
    rel_std_dev = _StatsProperty('rel_std_dev', _calc_rel_std_dev)

    def _calc_skewness(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default
    skewness = _StatsProperty('skewness', _calc_skewness)

    def _calc_kurtosis(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0
    kurtosis = _StatsProperty('kurtosis', _calc_kurtosis)

    def _calc_pearson_type(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')
    pearson_type = _StatsProperty('pearson_type', _calc_pearson_type)

    @staticmethod
    def _get_quantile(sorted_data, q):
        data, n = sorted_data, len(sorted_data)
        idx = q / 1.0 * (n - 1)
        idx_f, idx_c = int(floor(idx)), int(ceil(idx))
        if idx_f == idx_c:
            return data[idx_f]
        return (data[idx_f] * (idx_c - idx)) + (data[idx_c] * (idx - idx_f))

    def get_quantile(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def get_zscore(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def trim_relative(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def _get_pow_diffs(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v - m) ** power for v in self.data]

    def _get_bin_bounds(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def get_histogram_counts(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def format_histogram(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def describe(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret


def describe(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(quantiles=quantiles, format=format)


def _get_conv_func(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       attr_name)
    return stats_helper


for attr_name, attr in list(Stats.__dict__.items()):
    if isinstance(attr, _StatsProperty):
        if attr_name in ('max', 'min', 'count'):  # don't shadow builtins
            continue
        if attr_name in ('mad',):  # convenience aliases
            continue
        func = _get_conv_func(attr_name)
        func.__doc__ = attr.func.__doc__
        globals()[attr_name] = func
        delattr(Stats, '_calc_' + attr_name)
# cleanup
del attr
del attr_name
del func


def format_histogram_counts(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)
