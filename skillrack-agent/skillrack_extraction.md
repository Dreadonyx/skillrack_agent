# Skillrack Problem — Full Text Extraction

## Problem Statement

There are N servers handling requests which are numbered from 1 to N. Each request takes different time to complete. The requests are sent to servers in round robin fashion. If a server has failed, then the unprocessed requests are sent to the remaining servers.

Series of M event details are passed as the input to the program. The event details can be any of the following types:

**Type I** - If the event type is R, a new request is sent along with the timestamp T1 (in seconds) at which the request is sent to the server and the timestamp T2 (in seconds) which is the time taken to process the request by the server.

**Type II** - If the event type is F, the server has failed with the server id and the timestamp T1 (in seconds) at which the server has failed.

At the end of all the events, the program must print the maximum number of requests processed among the N servers as the output.

**Note:** In round robin fashion, sending requests to the servers always starts from the server 1. At least one server is always running after N events.

### Boundary Condition(s)
- 1 <= N <= 100
- 1 <= M <= 1000
- 1 <= T1, T2 <= 10^8

### Input Format
The first line contains the values of N and M separated by a space.
The next M lines contain the event details as mentioned above.

### Output Format
The first line contains the maximum number of requests processed among the N servers.

### Example Input/Output 1

**Input:**
```
3 7
R 1 10
R 1 12
R 1 14
R 2 5
R 15 10
R 16 12
F 3 17
```

**Output:**
```
3
```

**Explanation:**
Second 1: (R 1 10) processing on the server 1. (R 1 12) processing on the server 2. (R 1 14) processing on the server 3.
Second 2: (R 1 9), (R 2 5) processing on the server 1. (R 1 11) processing on the server 2. (R 1 13) processing on the server 3.
Second 3: (R 1 8), (R 2 5) processing on the server 1. (R 1 10) processing on the server 2. (R 1 12) processing on the server 3.
Second 4: (R 1 7), (R 2 5) processing on the server 1. (R 1 9) processing on the server 2. (R 1 11) processing on the server 3.
Second 5: (R 1 6), (R 2 5) processing on the server 1. (R 1 8) processing on the server 2. (R 1 10) processing on the server 3.
Second 6: (R 1 5), (R 2 5) processing on the server 1. (R 1 7) processing on the server 2. (R 1 9) processing on the server 3.
Second 7: (R 1 4), (R 2 5) processing on the server 1. (R 1 6) processing on the server 2. (R 1 8) processing on the server 3.
Second 8: (R 1 3), (R 2 5) processing on the server 1. (R 1 5) processing on the server 2. (R 1 7) processing on the server 3.
Second 9: (R 1 2), (R 2 5) processing on the server 1. (R 1 4) processing on the server 2. (R 1 6) processing on the server 3.
Second 10: (R 1 1), (R 2 5) processing on the server 1. (R 1 3) processing on the server 2. (R 1 5) processing on the server 3.
Second 11: (R 2 5) processing on the server 1. (R 1 2) processing on the server 2. (R 1 4) processing on the server 3.
Second 12: (R 2 4) processing on the server 1. (R 1 1) processing on the server 2. (R 1 3) processing on the server 3.
Second 13: (R 2 3) processing on the server 1. NO REQUEST processing on the server 2. (R 1 2) processing on the server 3.
Second 14: (R 2 2) processing on the server 1. NO REQUEST processing on the server 2. (R 1 1) processing on the server 3.
Second 15: (R 2 1) processing on the server 1. (R 15 10) processing on the server 2. NO REQUEST processing on the server 3.
Second 16: NO REQUEST processing on the server 1. (R 15 9) processing on the server 2. (R 16 12) processing on the server 3.
Second 17: (R 16 11) processing on the server 1. (R 15 7) processing on the server 2. Server 3 FAILED (R 16 12) has served to the server 1.
Second 18: (R 16 11) processing on the server 1. (R 15 7) processing on the server 2. Server 3 FAILED.
Second 19: (R 16 10) processing on the server 1. (R 15 6) processing on the server 2. Server 3 FAILED.
Second 20: (R 16 9) processing on the server 1. (R 15 5) processing on the server 2. Server 3 FAILED.
Second 22: (R 16 7) processing on the server 1. (R 15 3) processing on the server 2. Server 3 FAILED.
Second 23: (R 16 6) processing on the server 1. (R 15 2) processing on the server 2. Server 3 FAILED.
Second 24: (R 16 5) processing on the server 1. (R 15 1) processing on the server 2. Server 3 FAILED.
Second 25: (R 16 4) processing on the server 1. NO REQUEST processing on the server 2. Server 3 FAILED.
Second 26: (R 16 3) processing on the server 1. NO REQUEST processing on the server 2. Server 3 FAILED.
Second 27: (R 16 2) processing on the server 1. NO REQUEST processing on the server 2. Server 3 FAILED.
Second 28: (R 16 1) processing on the server 1. NO REQUEST processing on the server 2. Server 3 FAILED.

At the end of all the events, the server 1 has completed 3 requests, the server 2 has completed 2 requests and the server 3 has completed only one request. So the maximum number of requests processed among the 3 servers is 3. Hence 3 is printed as the output.

*(Note: the source screenshot's explanation jumps from "Second 20" to "Second 22" — Second 21 is not shown, likely omitted in the original.)*

### Example Input/Output 2

**Input:**
```
3 12
R 1 5
R 2 10
R 3 4
R 4 10
R 5 5
R 6 1
R 7 3
R 8 2
R 9 1
R 10 3
F 3 15
R 16 4
```

**Output:**
```
4
```

**Max Execution Time Limit:** 2000 millisec

---

## Submitted C Code

```c
#include<stdio.h>
#include<string.h>
#define MAXN 105
#define MAXQ 1005
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
    int i;
    for(i = 0; i < N; i++) {
        if(active[rr]) {
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
    int i;
    scanf("%d %d", &N, &M);
    for(i = 0; i < N; i++) {
        active[i] = 1;
        end_t[i] = 0;
        cnt[i] = 0;
        qsz[i] = 0;
    }
    rr = 0;
    int e;
    for(e = 0; e < M; e++) {
        char type;
        scanf(" %c", &type);
        if(type == 'R') {
            ll t1, t2;
            scanf("%lld %lld", &t1, &t2);
            int s = next_server();
            if(s != -1) assign_req(s, t1, t2);
        } else {
            int sid;
            ll ft;
            scanf("%d %lld", &sid, &ft);
            int completed = 0;
            int j;
            for(j = 0; j < qsz[sid]; j++) {
                if(req_end[sid][j] <= ft) completed++;
            }
            active[sid] = 0;
            int failover_ptr = (rr - 2) % N;
            for(j = 0; j < qsz[sid]; j++) {
                if(req_end[sid][j] > ft) {
                    int s = -1, k;
                    for(k = 0; k < N; k++) {
                        int cand = (failover_ptr + k) % N;
                        if(active[cand]) { s = cand; failover_ptr = (cand + 1) % N; break; }
                    }
                    if(s != -1) assign_req(s, ft, req_t2[sid][j]);
                }
            }
            cnt[sid] = completed;
            qsz[sid] = 0;
            end_t[sid] = 0;
        }
    }
    int maxcnt = 0;
    for(i = 0; i < N; i++) {
        if(cnt[i] > maxcnt) maxcnt = cnt[i];
    }
    printf("%d\n", maxcnt);
    return 0;
}
```

Footer text under code panel: `11322403201B@vee`

---

## Failing Hidden Test Case

Panel note: "You have used 1 reveals out of 2 in the past 7 Days."

**Input:**
```
13 1000
R 1 17
R 2 13
R 3 14
R 4 14
R 5 10
R 6 13
R 7 20
R 8 15
R 9 20
R 10 12
R 11 14
F 1 12
R 13 19
R 14 12
R 15 12
R 16 19
R 17 20
R 18 13
R 19 18
R 20 18
R 21 11
R 22 12
R 23 10
R 24 10
R 25 17
R 26 16
R 27 12
R 28 20
R 29 14
R 30 15
R 31 20
R 32 10
R 33 12
R 34 10
R 35 10
R 36 10
R 37 14
R 38 17
R 39 15
R 40 10
R 41 20
R 42 19
R 43 15
R 44 10
F 2 45
R 46 13
R 47 17
R 48 10
R 49 14
R 50 17
R 51 20
R 53 17
R 54 18
R 55 16
R 56 15
R 57 17
R 58 17
R 59 17
R 60 18
R 61 18
R 62 16
R 63 12
R 64 12
R 65 19
R 66 14
R 67 10
R 68 15
R 69 13
R 70 10
R 71 15
R 72 19
R 73 14
R 74 13
R 75 20
R 76 17
R 77 11
F 3 78
R 79 20
R 80 15
R 81 11
R 82 12
R 83 19
R 84 10
R 85 14
R 86 15
R 87 11
R 88 15
R 89 19
R 90 18
R 91 14
R 92 11
R 93 10
R 94 19
R 95 12
R 96 16
R 97 10
R 98 15
R 99 19
R 100 12
R 101 16
R 102 19
R 103 17
R 104 19
R 105 16
R 106 16
R 107 18
R 108 20
R 109 12
R 110 10
R 111 20
R 112 11
R 113 12
R 114 19
R 115 17
R 116 16
R 117 14
R 118 15
R 119 15
R 120 17
R 121 20
R 122 19
R 123 16
R 124 20
R 125 17
R 126 16
R 127 19
R 128 13
R 129 19
R 130 11
R 131 20
R 132 18
R 133 20
F 4 134
R 135 13
R 136 20
R 137 14
R 138 13
R 139 20
R 140 11
R 141 16
R 142 18
R 143 15
R 144 16
R 145 11
R 146 19
R 147 13
R 148 13
R 149 18
R 150 13
R 151 11
R 152 20
R 153 15
R 154 15
R 155 14
R 156 19
R 157 15
R 158 20
R 159 18
R 160 18
R 161 14
R 162 17
R 163 14
R 164 14
R 165 14
R 166 15
R 167 17
R 168 13
R 169 18
R 170 11
R 171 15
R 172 16
R 173 15
R 174 18
R 175 15
R 176 14
R 177 11
R 178 14
R 179 17
R 180 10
R 181 16
R 182 12
R 183 17
R 184 18
R 185 15
R 186 16
R 187 17
R 188 20
R 189 17
R 190 17
R 191 18
R 192 13
R 193 18
R 194 15
R 195 15
R 196 16
R 197 19
R 198 16
R 199 14
R 200 15
R 201 11
R 202 10
R 203 10
R 204 18
R 205 17
R 206 11
R 207 13
R 208 14
R 209 10
R 210 10
R 211 11
R 212 10
R 213 12
R 214 17
R 215 20
R 216 19
R 217 10
R 218 13
R 219 19
R 220 14
R 221 19
R 222 11
R 223 18
R 224 17
R 225 16
R 226 17
R 227 13
R 228 15
R 229 19
R 230 14
R 231 11
R 232 12
R 233 19
R 234 12
R 235 19
R 236 13
R 237 16
R 238 14
R 239 19
R 240 10
F 5 241
R 242 17
R 243 18
R 244 12
R 245 14
R 246 19
R 247 15
R 248 18
R 249 20
R 250 12
R 251 17
R 252 14
R 253 12
R 254 15
R 255 14
R 256 19
R 257 16
R 258 14
R 259 17
R 260 19
R 261 18
R 262 10
R 263 16
R 264 14
R 265 19
R 266 16
R 267 11
R 268 13
R 269 20
R 270 10
R 271 11
R 272 15
R 273 16
R 274 20
R 275 13
R 276 12
R 277 13
R 278 17
R 279 16
R 280 11
R 281 11
R 282 19
R 283 13
R 284 20
R 285 13
R 286 16
R 287 17
R 288 20
R 289 18
R 290 13
R 291 19
R 292 11
R 293 20
R 294 12
R 295 19
R 296 12
R 297 16
R 298 20
R 299 19
R 300 19
R 301 18
F 6 302
R 303 17
R 304 13
R 305 10
R 306 14
R 307 12
R 308 19
R 309 10
R 310 10
R 311 17
R 312 16
R 313 14
R 314 10
R 315 15
R 316 10
R 317 19
R 318 15
R 319 17
R 320 18
R 321 12
R 322 17
R 323 19
R 324 17
R 325 20
R 326 18
R 327 18
R 328 17
R 329 12
R 330 18
R 331 12
R 332 13
R 333 15
R 334 14
R 335 10
R 336 19
R 337 18
R 338 18
R 339 18
R 340 10
R 341 14
R 342 15
R 343 17
R 344 10
R 345 12
R 346 12
F 7 346
R 348 18
R 349 16
R 350 12
R 351 12
R 352 20
R 353 15
R 354 13
R 355 15
R 356 12
R 357 18
R 358 20
R 359 14
R 360 20
R 361 12
R 362 17
R 363 12
R 364 15
R 365 18
R 366 20
R 367 20
R 368 10
R 369 13
R 370 15
R 371 14
R 372 19
R 373 11
R 374 13
R 375 16
R 376 19
R 377 11
R 378 17
R 379 12
R 380 11
R 381 14
R 382 19
R 383 18
R 384 12
R 385 20
R 386 13
R 387 17
R 388 16
R 389 15
R 390 15
R 391 20
R 392 20
R 393 16
R 394 12
R 395 20
R 396 16
R 397 18
R 398 12
R 399 14
R 400 10
R 401 11
R 402 19
R 403 11
R 404 16
R 405 16
R 406 17
R 407 20
R 408 13
R 409 15
R 410 17
R 411 12
F 8 413
R 414 20
R 415 19
R 416 20
R 417 15
R 418 11
R 419 11
R 420 19
R 421 13
R 422 14
R 423 13
R 424 16
R 425 20
R 426 18
R 427 20
R 428 20
R 429 12
R 430 19
R 431 13
R 432 18
R 433 16
R 434 12
R 435 14
R 436 17
R 437 17
R 438 12
R 439 17
R 440 15
R 441 19
R 442 10
R 443 20
R 444 13
R 445 19
R 446 19
R 447 10
R 448 13
R 449 20
R 450 10
R 451 11
R 452 15
R 453 13
R 454 20
R 455 17
R 456 11
R 457 17
R 458 14
R 459 16
R 460 15
R 461 15
R 462 19
R 463 17
R 464 14
R 465 16
R 466 13
R 467 16
R 468 14
R 469 19
R 470 17
R 471 13
R 472 13
R 473 12
R 474 18
R 475 16
R 476 14
R 477 20
R 478 13
R 479 15
R 480 20
R 481 12
R 482 15
R 483 15
R 484 13
R 485 10
R 486 13
R 487 16
R 488 18
R 489 20
R 490 10
R 491 11
R 492 10
R 493 20
R 494 11
R 495 10
R 496 10
R 497 19
R 498 19
R 499 14
R 500 18
R 501 12
R 502 11
R 503 19
R 504 15
R 505 16
R 506 19
R 507 10
R 508 16
R 509 17
R 510 13
R 511 14
R 512 11
R 513 11
R 514 16
R 515 14
R 516 11
R 517 12
R 518 11
R 519 16
R 520 13
R 521 11
R 522 19
R 523 10
R 524 13
R 525 12
R 526 17
R 527 17
R 528 10
R 529 18
R 530 18
R 531 14
R 532 20
R 533 13
R 534 19
R 535 12
R 536 15
R 537 14
R 538 11
R 539 11
R 540 14
R 541 12
R 542 18
R 543 17
R 544 18
R 545 20
R 546 15
R 547 12
R 548 17
R 549 11
R 550 12
R 551 16
R 552 20
R 553 18
R 554 16
R 555 18
R 556 10
R 557 19
R 558 14
R 559 16
R 560 18
R 561 17
R 562 12
R 563 15
R 564 12
R 565 19
R 566 10
R 567 11
R 568 14
R 569 13
R 570 18
R 571 13
R 572 20
R 573 20
R 574 19
R 575 18
R 576 12
R 577 18
R 578 17
R 579 19
R 580 10
R 581 18
R 582 18
R 583 18
R 584 13
R 585 19
R 586 14
R 587 13
F 9 588
R 589 14
R 590 12
R 591 17
R 592 20
R 593 10
R 594 16
R 595 13
R 596 14
R 597 14
R 598 10
R 599 17
R 600 11
R 601 12
R 602 10
R 603 13
R 604 16
R 605 20
R 606 18
R 607 13
R 608 10
R 609 18
R 610 17
R 611 11
R 612 11
R 613 16
R 614 10
R 615 17
R 616 13
R 617 15
R 618 16
R 619 12
R 620 14
R 621 12
R 622 12
R 623 12
R 624 20
R 625 18
R 626 14
R 627 10
R 628 13
R 629 16
R 630 19
R 631 12
R 632 15
R 633 15
R 634 14
R 635 18
R 636 17
R 637 13
R 638 13
R 639 12
R 640 17
R 641 10
R 642 13
F 10 643
R 644 11
R 645 13
R 646 12
R 647 10
R 648 10
R 649 12
R 650 12
R 651 20
R 652 10
R 653 14
R 654 13
R 655 12
R 656 19
R 657 18
R 658 14
R 659 12
R 660 20
R 661 10
R 662 10
R 663 12
R 664 13
R 665 13
R 666 10
R 667 16
R 668 12
R 669 12
R 670 17
R 671 18
R 672 14
R 673 17
R 674 19
R 675 14
R 676 10
R 677 12
R 678 14
R 679 16
R 680 16
R 681 13
R 682 12
R 683 17
R 684 20
R 685 13
R 686 13
R 687 20
R 688 14
R 689 17
R 690 13
R 691 16
R 692 10
R 693 17
R 694 15
R 695 15
R 696 11
R 697 20
R 698 17
R 699 12
R 700 12
R 701 13
R 702 17
R 703 19
R 704 19
R 705 17
R 706 11
F 11 707
R 708 14
R 709 14
R 710 19
R 711 17
R 712 16
R 713 16
R 714 12
R 715 18
R 716 15
R 717 20
R 718 10
R 719 19
R 720 19
R 721 12
R 722 14
R 723 19
R 724 15
R 725 19
R 726 16
R 727 10
R 728 18
R 729 14
R 730 14
R 731 15
R 732 18
R 733 14
R 734 10
R 735 10
R 736 14
R 737 17
R 738 14
R 739 17
R 740 19
R 741 13
R 742 15
R 743 19
R 744 10
R 745 11
R 746 16
R 747 18
R 748 16
R 749 20
R 750 15
R 751 13
R 752 17
R 753 12
R 754 16
R 755 19
R 756 13
R 757 15
R 758 19
R 759 15
R 760 12
R 761 11
R 762 11
R 763 11
R 764 16
R 765 15
R 766 11
R 767 13
R 768 14
R 769 20
R 770 17
R 771 10
R 772 17
F 12 773
R 774 12
R 775 18
R 776 20
R 777 15
R 778 15
R 779 11
R 780 16
R 781 11
R 782 20
R 783 11
R 784 10
R 785 11
R 786 17
R 787 14
R 788 17
R 789 10
R 790 10
R 791 12
R 792 19
R 793 10
R 794 13
R 795 10
R 796 16
R 797 13
R 798 17
R 799 15
R 800 11
R 801 20
R 802 17
R 803 10
R 804 17
R 805 13
R 806 15
R 807 10
R 808 12
R 809 18
R 810 13
R 811 12
R 812 18
R 813 13
R 814 11
R 815 12
R 816 14
R 817 10
R 818 10
R 819 17
R 820 19
R 821 16
R 822 18
R 823 13
R 824 17
R 825 19
R 826 10
R 827 16
R 828 15
R 829 10
R 830 15
R 831 18
R 832 18
R 833 13
R 834 16
R 835 18
R 836 17
R 837 19
R 838 19
R 839 16
R 840 10
R 841 16
R 842 15
R 843 20
R 844 13
R 845 16
R 846 17
R 847 12
R 848 11
R 849 10
R 850 13
R 851 15
R 852 14
R 853 14
R 854 12
R 855 19
R 856 19
R 857 16
R 858 16
R 859 11
R 860 12
R 861 11
R 862 19
R 863 13
R 864 19
R 865 18
R 866 17
R 867 17
R 868 10
R 869 17
R 870 19
R 871 14
R 872 10
R 873 11
R 874 13
R 875 12
R 876 17
R 877 17
R 878 12
R 879 11
R 880 20
R 881 14
R 882 14
R 883 19
R 884 17
R 885 20
R 886 10
R 887 18
R 888 20
R 889 17
R 890 13
R 891 14
R 892 15
R 893 19
R 894 10
R 895 11
R 896 13
R 897 19
R 898 17
R 899 14
R 900 18
R 901 12
R 902 20
R 903 16
R 904 12
R 905 13
R 906 19
R 907 20
R 908 19
R 909 14
R 910 10
R 911 17
R 912 17
R 913 20
R 914 19
R 915 13
R 916 19
R 917 15
R 918 12
R 919 14
R 920 19
R 921 15
R 922 16
R 923 20
R 924 10
R 925 16
R 926 15
R 927 18
R 928 17
R 929 16
R 930 20
R 931 13
R 932 10
R 933 20
R 934 14
R 935 13
R 936 11
R 937 17
R 938 20
R 939 16
R 940 15
R 941 20
R 942 18
R 943 17
R 944 10
R 945 17
R 946 15
R 947 12
R 948 20
R 949 13
R 950 16
R 951 18
R 952 18
R 953 17
R 954 18
R 955 14
R 956 14
R 957 18
R 958 18
R 959 20
R 960 19
R 961 12
R 962 16
R 963 10
R 964 10
R 965 13
R 966 20
R 967 15
R 968 19
R 969 15
R 970 20
R 971 13
R 972 16
R 973 10
R 974 15
R 975 16
R 976 16
R 977 10
R 978 17
R 979 16
R 980 10
R 981 11
R 982 13
R 983 19
R 984 19
R 985 12
R 986 19
R 987 11
R 988 14
R 989 12
R 990 20
R 991 17
R 992 15
R 993 13
R 994 17
R 995 11
R 996 14
R 997 17
R 998 12
R 999 17
R 1000 18
```

**Expected Output:**
```
945
```

**Your Program Output:**
```
717
```

**Result:** 4 Private (Hidden) Test Cases Failed. — 8 Passed, 4 Failed.

---

## Transcription notes
- A few event-number lines appear to be clipped exactly at screenshot page breaks (e.g., around R 51/R 52/R 53, R 346/R 347/R 348, R 411/R 412, and "Second 20"/"Second 21"/"Second 22" in the explanation). These are artifacts of how the scrolling code editor was screenshotted in slices — I've transcribed exactly what's visible in each image without inventing missing lines.
- The line `11322403201B@vee` appears at the very bottom of the code editor pane — likely an autosave/session ID string rather than part of the program.
