"""
Solutions database for Python Course problems.
Returns complete Python code for a given PID.
"""
def get(pid, template=None, problem_text=""):
    pid = str(pid)

    # ─── H013 Files ───────────────────────────────────────
    if pid == "2904":
        return 'f=open("output.txt","a")\nf.write("Actor3 - IJKL")\nf.close()'
    if pid == "2905":
        return 'f=open("fruits.txt","a")\nf.write("Mango")\nf.close()'
    if pid == "2906":
        return 'f=open("country.txt","a")\nf.write("\\nIndia")\nf.close()'
    if pid == "2907":
        return 'f=open("output.txt","a")\nf.writelines(["Cherry\\n","Mango\\n"])\nf.close()'
    if pid == "2908":
        return 'f1=open("source.txt")\nf2=open("target.txt","a")\nf2.write(f1.read())\nf1.close()\nf2.close()'
    if pid == "2909":
        return 'f=open("output.txt","a")\nf.write("Line1\\nLine2\\nLine3")\nf.close()'
    if pid == "2910":
        return 's=input()\nf=open("output.txt","a")\nf.write(s)\nf.close()'
    if pid == "2911":
        return 'f=open("output.txt","a")\nf.write("\\nHello World")\nf.close()'
    if pid == "2912":
        return 'f1=open("input.txt")\ndata=f1.read()\nf1.close()\nf2=open("output.txt","a")\nf2.write(data)\nf2.close()'

    # ─── H014 Classes & Objects ──────────────────────────
    if pid == "2913":
        return 'class Car:\n    def __init__(self,brand,model):\n        self.brand=brand\n        self.model=model\n    def display(self):\n        print(self.brand,self.model)'
    if pid == "2914":
        return 'class Student:\n    def __init__(self,name,marks):\n        self.name=name\n        self.marks=marks\n    def display(self):\n        print(self.name,self.marks)'
    if pid == "2915":
        return 'class Rectangle:\n    def __init__(self,l,b):\n        self.l=l\n        self.b=b\n    def area(self):\n        return self.l*self.b'
    if pid == "2916":
        return 'class Circle:\n    def __init__(self,r):\n        self.r=r\n    def area(self):\n        return 3.14*self.r*self.r'
    if pid == "2917":
        return 'class BankAccount:\n    def __init__(self,bal=0):\n        self.bal=bal\n    def deposit(self,a):\n        self.bal+=a\n    def withdraw(self,a):\n        if a<=self.bal:\n            self.bal-=a'
    if pid == "2918":
        return 'class Employee:\n    def __init__(self,n,s):\n        self.name=n\n        self.salary=s\n    def display(self):\n        print(self.name,self.salary)'
    if pid == "2919":
        return 'class Book:\n    def __init__(self,t,a):\n        self.title=t\n        self.author=a\n    def display(self):\n        print(self.title,self.author)'
    if pid == "2920":  # H014 override
        return 'class B(A):\n    def display(self):\n        print("B class")'
    if pid == "2921":  # H014 hidden variable
        return 'print (c._Country__population)'

    # ─── H015 Fill-in-blanks (course problems) ──────────
    if pid == "2922":  # pass
        return '        pass'
    if pid == "2923":  # break
        return '    if num%9 == 0:\n        break'
    if pid == "2924":  # x=6, y=20
        return 'x = 6\ny = 20'

    # ─── H015 Regular problems ──────────────────────────
    if pid == "2925":
        return 'n=int(input())\nif n%2==0:\n    print("Even")\nelse:\n    print("Odd")'
    if pid == "2926":
        return 'n=int(input())\nf=1\nfor i in range(1,n+1):\n    f*=i\nprint(f)'
    if pid == "2927":
        return 'n=int(input())\nif n>0:\n    print("Positive")\nelif n<0:\n    print("Negative")\nelse:\n    print("Zero")'
    if pid == "2928":
        return 'n=int(input())\ns=0\nwhile n>0:\n    s+=n%10\n    n//=10\nprint(s)'
    if pid == "2929":
        return 'n=input()\nif n==n[::-1]:\n    print("Palindrome")\nelse:\n    print("Not Palindrome")'
    if pid == "2930":
        return 'n=int(input())\nc=0\nfor i in range(1,n+1):\n    if n%i==0:\n        c+=1\nprint(c)'

    # ─── H014 Fill-in-blanks ────────────────────────────
    if pid == "2912":  # Employee __del__
        return '    def __del__(self):\n        print(self.salary-self.salary*2)'
    if pid == "2916":  # Circle MRO fix
        return '        return abs(self.r - other.r)'

    # ─── Easy Challenges (PART004) ──────────────────────
    if pid == "2598":  # First Letter In Word - Uppercase
        return 's=input().split()\nfor w in s:\n    print(w[0].upper(),end="")'
    if pid == "2599":  # Difference between rectangle lengths
        return 'a1, a2 = map(int, input().split())\nw1, w2 = map(int, input().split())\nl1 = (a1 / 5) / w1\nl2 = (a2 / 5) / w2\nprint(f"{abs(l1 - l2):.2f}")'
    if pid == "2600":  # Calendar Month
        return 'd = input().strip()\nmonths = ["January","February","March","April","May","June","July","August","September","October","November","December"]\nprint(months[int(d.split("-")[1]) - 1])'

    # ─── Easy Challenges (PART003) ──────────────────────
    if pid == "2582":  # Betting game - Dice roll
        return 'd = list(map(int, input().split()))\nx = int(input())\ny = int(input())\nodd = sum(1 for n in d if n % 2 != 0)\neven = sum(1 for n in d if n % 2 == 0)\nprint(odd * x - even * y)'
    if pid == "2583":  # Count of common characters in two strings
        return 's1 = input().strip()\ns2 = input().strip()\nprint(len(set(s1) & set(s2)))'
    if pid == "2584":  # Reverse String Till Underscore
        return 's = input().strip()\nif "_" in s:\n    i = s.index("_")\n    print(s[:i][::-1] + s[i:])\nelse:\n    print(s[::-1])'
    if pid == "2585":  # Expand Alphabets
        return 's = input().strip()\nout = ""\ni = 0\nwhile i < len(s):\n    n = ""\n    while i < len(s) and s[i].isdigit():\n        n += s[i]\n        i += 1\n    c = s[i]\n    i += 1\n    out += c * int(n)\nprint(out)'
    if pid == "2586":  # Simple Calculator Command
        return 's = input().strip()\nfor ch in s:\n    if ch.isalpha():\n        parts = s.split(ch)\n        a, b = int(parts[0]), int(parts[1]) if len(parts) > 1 else int(ch + parts[1])\n        op = ch.lower()\n        if op == "a": print(a + b)\n        elif op == "s": print(a - b)\n        elif op == "m": print(a * b)\n        elif op == "d": print(a // b)\n        break'
    if pid == "2587":  # Convert rupee to paise
        return 's = input().strip()\nif "." in s:\n    parts = s.split(".")\n    rupee = int(parts[0])\n    paise_str = parts[1][:2].ljust(2, "0")\n    print(rupee * 100 + int(paise_str))\nelse:\n    print(int(s) * 100)'
    if pid == "2588":  # Head Count - Birds and Animals
        return 'h = int(input())\nl = int(input())\na = (l - 2*h) // 2\nb = h - a\nprint(b, a)'
    if pid == "2589":  # Count of common factors
        return 'n = int(input())\nnums = [int(input()) for _ in range(n)]\nm = min(nums)\nc = 0\nfor i in range(2, m + 1):\n    if all(x % i == 0 for x in nums):\n        c += 1\nprint(c)'
    if pid == "2590":  # Reverse Number Sign
        return 'n = int(input())\nprint(-n)'

    # ─── Easy Challenges (PART002) ──────────────────────
    if pid == "2578":  # Lowest Mileage Car
        return 'cars = input().split()\nmin_car = None\nmin_m = float("inf")\nfor c in cars:\n    name, m = c.split("@")\n    m = float(m)\n    if m < min_m:\n        min_m = m\n        min_car = name\nprint(min_car)'
    if pid == "2579":  # Palindrome Missing Alphabet
        return 's = input().strip()\ni, j = 0, len(s) - 1\nwhile i < j:\n    if s[i] == s[j]:\n        i += 1\n        j -= 1\n    else:\n        if s[i+1] == s[j]:\n            print(s[i])\n        else:\n            print(s[j])\n        break'
    if pid == "2580":  # Pattern Printing - Half Pyramid Numbers
        return 'n = int(input())\nfor i in range(1, n + 1):\n    for j in range(1, i + 1):\n        if j == i:\n            print(j)\n        else:\n            print(j, end=" ")'

    # ─── Data Structures - Queue ────────────────────────────
    if pid == "8804":  # Queue - Round Robin
        return '''#include<stdio.h>

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
        } else {
            int sid;
            ll ft;
            scanf("%d %lld", &sid, &ft);
            sid--;

            int completed = 0;
            for (int j = 0; j < qsz[sid]; j++)
                if (req_end[sid][j] <= ft) completed++;

            active[sid] = 0;

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

    printf("%d\\n", maxcnt);
    return 0;
}'''

    if pid == "8812":  # Queue - Railway Station
        return '''#include <stdio.h>
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
    printf("%lld\\n", mx);
    
    for (int i = 0; i < N; i++) free(q[i]);
    free(q); free(qh); free(qt);
    free(active); free(completed);
    free(events);
    return 0;
}'''

    return None
