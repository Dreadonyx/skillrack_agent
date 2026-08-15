#include <stdio.h>

#define MAXN 105
#define MAXQ 2005
typedef long long ll;

int N, M;
int active[MAXN];
ll end_t[MAXN];
int cnt[MAXN];
ll req_t2[MAXN][MAXQ];
ll req_end[MAXN][MAXQ];
int qsz[MAXN];
int rr;

int next_server() {
    for (int i = 0; i < N; i++) {
        if (active[rr]) {
            int s = rr;
            rr = (rr + 1) % N;
            return s;
        }
        rr = (rr + 1) % N;
    }
    return -1;
}

void assign_req(int s, ll t1, ll t2) {
    ll st = (end_t[s] > t1) ? end_t[s] : t1;
    ll en = st + t2;
    req_t2[s][qsz[s]] = t2;
    req_end[s][qsz[s]] = en;
    qsz[s]++;
    end_t[s] = en;
    cnt[s]++;
}

int main() {
    scanf("%d %d", &N, &M);
    for (int i = 0; i < N; i++) {
        active[i] = 1;
        end_t[i] = 0;
        cnt[i] = 0;
        qsz[i] = 0;
    }
    rr = 0;

    for (int e = 0; e < M; e++) {
        char type;
        scanf(" %c", &type);
        if (type == 'R') {
            ll t1, t2;
            scanf("%lld %lld", &t1, &t2);
            int s = next_server();
            if (s != -1) assign_req(s, t1, t2);
        } else { // type == 'F'
            int sid;
            ll ft;
            scanf("%d %lld", &sid, &ft);
            sid--; // convert 1-indexed input to 0-indexed

            int completed = 0;
            for (int j = 0; j < qsz[sid]; j++)
                if (req_end[sid][j] <= ft) completed++;

            active[sid] = 0;

            // reassign unfinished requests via separate round-robin (independent of rr)
            int fptr = rr;
            for (int j = 0; j < qsz[sid]; j++) {
                if (req_end[sid][j] > ft) {
                    ll remaining = req_end[sid][j] - ft;
                    if (remaining > req_t2[sid][j]) remaining = req_t2[sid][j];
                    int s2 = -1;
                    for (int k = 0; k < N; k++) {
                        int cand = (fptr + k) % N;
                        if (active[cand]) { s2 = cand; fptr = (cand + 1) % N; break; }
                    }
                    if (s2 != -1) assign_req(s2, ft, remaining);
                }
            }

            cnt[sid] = completed;
            qsz[sid] = 0;
            end_t[sid] = 0;
        }
    }

    int maxcnt = 0;
    for (int i = 0; i < N; i++)
        if (cnt[i] > maxcnt) maxcnt = cnt[i];

    printf("%d\n", maxcnt);
    return 0;
}
