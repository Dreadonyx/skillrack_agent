#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char type;
    int id;
    long long at;
    long long bt;
    int idx;
} C;

int cmp(const void *a, const void *b) {
    C *c1 = (C *)a, *c2 = (C *)b;
    if (c1->at != c2->at) return c1->at < c2->at ? -1 : 1;
    return c1->idx < c2->idx ? -1 : 1;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    C *c = (C *)malloc(sizeof(C) * n);
    for (int i = 0; i < n; i++) {
        scanf(" %c %d %lld %lld", &c[i].type, &c[i].id, &c[i].at, &c[i].bt);
        c[i].idx = i;
    }
    
    qsort(c, n, sizeof(C), cmp);
    
    int *sq = (int *)malloc(sizeof(int) * n);
    int *nq = (int *)malloc(sizeof(int) * n);
    int sh = 0, st = 0, nh = 0, nt = 0;
    int nxt = 0;
    long long ct = 0;
    char last = 0;
    int done = 0;
    
    while (done < n) {
        if (sh == st && nh == nt) {
            if (nxt < n && c[nxt].at > ct) ct = c[nxt].at;
        }
        
        while (nxt < n && c[nxt].at <= ct) {
            if (c[nxt].type == 'S') sq[st++] = nxt;
            else nq[nt++] = nxt;
            nxt++;
        }
        
        int both = (sh < st && nh < nt);
        int pick = -1;
        
        if (both) {
            if (last == 0) {
                long long sa = c[sq[sh]].at;
                long long na = c[nq[nh]].at;
                if (sa < na) pick = sq[sh++];
                else if (na < sa) pick = nq[nh++];
                else pick = sq[sh++];
            } else if (last == 'S') {
                pick = nq[nh++];
            } else {
                pick = sq[sh++];
            }
            last = c[pick].type;
        } else if (sh < st) {
            pick = sq[sh++];
        } else if (nh < nt) {
            pick = nq[nh++];
        }
        
        if (pick != -1) {
            ct += c[pick].bt;
            done++;
            printf("%d%c", c[pick].id, done == n ? 10 : 32);
            if (sh == st && nh == nt) last = 0;
        }
    }
    
    free(c); free(sq); free(nq);
    return 0;
}