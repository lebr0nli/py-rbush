#ifndef _RBUSH_H_
#define _RBUSH_H_

class RBush {
public:
    RBush(int max_entries = 9);

private:
    int _max_entries;
    int _min_entries;
};

#endif // _RBUSH_H_