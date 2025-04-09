from core.core import Core

# Warning: evil things ahead
#
#
# Here we use global variables to store the core state :
# benchmarks, runners, results, etc... This is of course
# recommended against in various documentation (see for example
# https://dash.plotly.com/sharing-data-between-callbacks#why-global-variables-will-break-your-app ).
#
# BUT, the data is mostly read only, and is intended to be used
# by few users at a time. Things {c,sh}ould be fine if we are careful.


core = Core()
