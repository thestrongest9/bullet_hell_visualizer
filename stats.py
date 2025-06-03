import pstats
from pstats import SortKey
p = pstats.Stats('last.stats')
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(0.1)

#how to use the stats (cProfile) checker:
#   run python -m cProfile -o last.stats main.py
#Then you need to send this to file format
#   python stats.py > report.txt
#You should be able to read the profiler output in report.txt