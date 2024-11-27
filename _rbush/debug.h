#ifndef DEBUG_H_
#define DEBUG_H_

#ifdef RBUSH_DEBUG

#include <chrono>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>

#define DEBUG_TIMER(method_name) debug::Timer timer_##__LINE__(method_name)

namespace debug {

class RuntimeTracker {
public:
    static RuntimeTracker &get_instance() {
        static RuntimeTracker instance;
        return instance;
    }

    void log_time(const std::string &method_name, double duration) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto &data = _method_stats[method_name];
        data.count++;
        data.total_time += duration;
    }

    double get_avg_time(const std::string &method_name) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = _method_stats.find(method_name);
        if (it != _method_stats.end()) {
            return it->second.total_time / it->second.count;
        }
        return 0;
    }

    double get_total_time(const std::string &method_name) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = _method_stats.find(method_name);
        if (it != _method_stats.end()) {
            return it->second.total_time;
        }
        return 0;
    }

private:
    struct Stats {
        int count = 0;
        double total_time = 0;
    };

    std::unordered_map<std::string, Stats> _method_stats;
    mutable std::mutex mutex_;

    RuntimeTracker() = default;
    RuntimeTracker(const RuntimeTracker &) = delete;
    RuntimeTracker &operator=(const RuntimeTracker &) = delete;
};

class Timer {
public:
    Timer(const std::string &method_name)
        : _method_name(method_name), _start(std::chrono::high_resolution_clock::now()) {}

    ~Timer() {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - _start).count();
        RuntimeTracker::get_instance().log_time(_method_name, static_cast<double>(duration) / 1000);
    }

private:
    std::string _method_name;
    std::chrono::time_point<std::chrono::high_resolution_clock> _start;
};

} // namespace debug

#else

#define DEBUG_TIMER(methodName)

#endif // RBUSH_DEBUG

#endif // DEBUG_H_
