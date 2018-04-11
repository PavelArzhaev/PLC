#pragma once
#include <iostream>
#include <csetjmp>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <algorithm>

#define Excp1 (1)
#define Excp2 (2)


int level = -1;
std::jmp_buf buf_arr[10000];
class Obj;
std::vector<Obj*> obj_arr[10000];


class Obj {
public:
    Obj() {
        printf("Obj created");
        obj_arr[level].push_back(this);
    }
    ~Obj() {
        printf("Obj deleted");
    }
};

#define TRY_START { ++level; obj_arr[level].clear(); \
    int excpt_flag = setjmp(buf_arr[level]); switch (excpt_flag) { \
        case 0:

#define TRY_END break; default: --level; if (level < 0) {exit(-1);} \
            std::longjmp(buf_arr[level], excpt_flag); } }

#define EXCEPT(excpt_flag) break; case excpt_flag: --level;


#define RAISE(excpt_flag) { if (level < 0) {exit(-1);} \
    std::reverse(obj_arr[level].begin(), obj_arr[level].end()); \
    for (auto i: obj_arr[level]) { i->~Obj(); } \
    std::longjmp(buf_arr[level], excpt_flag); }