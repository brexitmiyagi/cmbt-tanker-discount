# the war-money screen, corrected for where each company books profit shares.
# CMB.TECH's Q3 2026 release puts the 'including profit share where applicable' footnote on the Suezmax SPOT rate and
# not on the Suezmax time charter rate, so its $32,986 a day is the base rate only and any profit split earned by
# its chartered Suezmaxes sits inside the $148,540 spot figure. Frontline, DHT and INSW book profit shares in the
# time charter line (data/profit_share_booking_q3_2026.csv), so their rows already net it off.
# so the old CMB.TECH Suezmax line (spot minus base, times charter days) is an upper bound. two ways to bring it down:
#   A. peer benchmark: CMB.TECH's Suezmax spot ran well above three peers' pure spot. treat the excess as profit
#      share paid to the chartered ships, and use the peer average as the market rate the charters gave up.
#   B. a 50/50 split above the base rate on the profit-split ships' days, solving for CMB.TECH's own pure spot.
# spot days aren't disclosed; I estimate them from the fleet and test a range.
from common import rows
peers = [float(r['suezmax_spot_tce_q3_2026']) for r in rows('suezmax_spot_peers_q3_2026.csv')]
S_peer = sum(peers) / len(peers)
R, base, tc_days = 148540.0, 32986.0, 717.0
vlcc = (149945 - 85623) * 92 / 1e6          # VLCC line unchanged: its time charter rate already includes profit share
old = (R - base) * tc_days / 1e6 + vlcc
print(f'old CMB.TECH figure: ${old:.1f}m (Suezmax ${old-vlcc:.1f}m + VLCC ${vlcc:.1f}m)')
print(f'peer Suezmax spot, Q3 2026: ' + ', '.join(f'{x:,.0f}' for x in peers) + f'; average ${S_peer:,.0f}; CMB.TECH reported ${R:,.0f} including profit share')
out = {}
for sd in (650, 780, 900):
    share_A = (R - S_peer) * sd / 1e6
    gap_A = (S_peer - base) * tc_days / 1e6 - share_A
    for psd in (82, 399):
        share_B = 0.5 * (R - base) * psd / (1 + 0.5 * psd / sd) / 1e6
        S_own = R - share_B * 1e6 / sd
        gap_B = (S_own - base) * tc_days / 1e6 - share_B
        out[(sd, psd)] = (gap_A + vlcc, gap_B + vlcc)
        print(f'spot days {sd}, profit-split ship-days {psd}: A (peer benchmark) profit share ${share_A:.1f}m, CMB.TECH total ${gap_A+vlcc:.1f}m; '
              f'B (50/50 split) profit share ${share_B:.1f}m, own pure spot ${S_own:,.0f}, total ${gap_B+vlcc:.1f}m')
lo = min(min(v) for v in out.values()); hi = max(max(v) for v in out.values())
print(f'range across methods and day counts: ${lo:.0f}m to ${hi:.0f}m, against ${old:.1f}m before')
print('82 profit-split ship-days counts only the two charters the Q1 2026 release says carry a split (Cap Grace from 19 Jul, Cap Joseph from 23 Sep);'
      ' 399 adds four more that investor relations described to me (cited with their consent, 26 Nov 2026)')
others = {'Frontline': 77.7, 'DHT Holdings': 54.5, 'Hafnia': 52.1, 'Scorpio Tankers': 40.6, 'Teekay Tankers': 20.7}
mid = out[(780, 82)][0]
rank = sorted(list(others.items()) + [('CMB.TECH (peer-benchmark, 780 days)', mid)], key=lambda x: -x[1])
print('ranking with the corrected CMB.TECH figure: ' + ', '.join(f'{n} ${v:.0f}m' for n, v in rank))
