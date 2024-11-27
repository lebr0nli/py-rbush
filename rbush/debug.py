import _rbush

if not hasattr(_rbush, "get_avg_time"):
    raise NotImplementedError("You need to build with RBUSH_DEBUG=1 to use this module.")

get_avg_time = _rbush.get_avg_time
get_total_time = _rbush.get_total_time

__all__ = ["get_avg_time", "get_total_time"]
