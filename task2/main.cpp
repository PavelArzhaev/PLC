#include "main.h"

void func() {
    Obj obj1 = Obj();
    RAISE(Excp1);
}

int main() {
    TRY_START {
        TRY_START {
            func();
        } EXCEPT(Excp1) {
            Obj obj2 = Obj();
            printf("func exception");
            RAISE(Excp2);
        } TRY_END
    } EXCEPT(Excp2) {
        printf("nested exception");
    } TRY_END
}