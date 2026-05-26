#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char type;
    long long svr;
    long long t1;
    long long t2;
    int idx;
} Event;

int cmp(const void *a, const void *b) {
    Event *e1 = (Event *)a, *e2 = (Event *)b;
    if (e1->t1 != e2->t1) return e1->t1 < e2->t1 ? -1 : 1;
    // Same time: R before F
    if (e1->type != e2->type) return e1->type == 'R' ? -1 : 1;
    return e1->idx < e2->idx ? -1 : 1;
}

int main() {
    int N, M;
    if (scanf("%d %d", &N, &M) != 2) return 0;
    
    Event *events = (Event *)malloc(sizeof(Event) * M);
    for (int i = 0; i < M; i++) {
        char type[2];
        scanf(" %s %lld", type, &events[i].t1);
        events[i].type = type[0];
        if (events[i].type == 'R') {
            scanf("%lld", &events[i].t2);
            events[i].svr = 0;
        } else {
            events[i].svr = events[i].t1;
            scanf("%lld", &events[i].t1);
            events[i].t2 = 0;
        }
        events[i].idx = i;
    }
    
    qsort(events, M, sizeof(Event), cmp);
    
    long long **q = (long long **)malloc(sizeof(long long *) * N);
    int *qh = (int *)calloc(N, sizeof(int));
    int *qt = (int *)calloc(N, sizeof(int));
    for (int i = 0; i < N; i++) {
        q[i] = (long long *)malloc(sizeof(long long) * M);
    }
    
    int *active = (int *)malloc(sizeof(int) * N);
    long long *completed = (long long *)calloc(N, sizeof(long long));
    for (int i = 0; i < N; i++) active[i] = 1;
    
    long long rr = 0;
    long long last_t = 0;
    
    for (int e = 0; e < M; e++) {
        long long cur_t = events[e].t1;
        long long dt = cur_t - last_t;
        
        if (dt > 0) {
            for (int i = 0; i < N; i++) {
                if (!active[i]) continue;
                long long rem = dt;
                while (qh[i] < qt[i] && rem > 0) {
                    if (q[i][qh[i]] <= rem) {
                        rem -= q[i][qh[i]];
                        qh[i]++;
                        completed[i]++;
                    } else {
                        q[i][qh[i]] -= rem;
                        rem = 0;
                    }
                }
            }
        }
        
        if (events[e].type == 'R') {
            long long serv_time = events[e].t2;
            int assigned = 0;
            for (int k = 0; k < N; k++) {
                int s = (int)((rr + k) % N);
                if (active[s]) {
                    q[s][qt[s]++] = serv_time;
                    rr = (s + 1) % N;
                    assigned = 1;
                    break;
                }
            }
            if (!assigned) {
                for (int k = 0; k < N; k++) {
                    if (active[k]) {
                        q[k][qt[k]++] = serv_time;
                        rr = (k + 1) % N;
                        break;
                    }
                }
            }
        } else {
            int fs = (int)(events[e].svr - 1);
            active[fs] = 0;
            long long *pending = (long long *)malloc(sizeof(long long) * (qt[fs] - qh[fs]));
            int pn = 0;
            for (int i = qh[fs]; i < qt[fs]; i++) {
                pending[pn++] = q[fs][i];
            }
            qh[fs] = qt[fs] = 0;
            
            for (int p = 0; p < pn; p++) {
                int assigned = 0;
                for (int k = 0; k < N; k++) {
                    int s = (int)((rr + k) % N);
                    if (active[s]) {
                        q[s][qt[s]++] = pending[p];
                        rr = (s + 1) % N;
                        assigned = 1;
                        break;
                    }
                }
                if (!assigned) break;
            }
            free(pending);
        }
        
        last_t = cur_t;
    }
    
    for (int i = 0; i < N; i++) {
        if (!active[i]) continue;
        long long rem = 1000000000000LL;
        while (qh[i] < qt[i] && rem > 0) {
            if (q[i][qh[i]] <= rem) {
                rem -= q[i][qh[i]];
                qh[i]++;
                completed[i]++;
            } else {
                q[i][qh[i]] -= rem;
                rem = 0;
            }
        }
    }
    
    long long mx = 0;
    for (int i = 0; i < N; i++) {
        if (completed[i] > mx) mx = completed[i];
    }
    printf("%lld\n", mx);
    
    for (int i = 0; i < N; i++) free(q[i]);
    free(q); free(qh); free(qt);
    free(active); free(completed);
    free(events);
    return 0;
}