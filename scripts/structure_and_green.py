# ownership, trading and the green fleet return test. inputs are typed in below with their sources.
sh_ex = 290.169769            # shares outside treasury (Q3 2026 release)
cmb = 178.726458              # CMB NV (20-F)
us_register = 88.297075       # shares on the US register, 1 April 2026 (20-F)
short = 3.207486              # shares short (Seeking Alpha metrics, latest reported as of 25 Nov 2026)
adv = 1.123362                # US average daily volume, 25 Aug to 24 Nov 2026 (Nasdaq historical)
float_ = sh_ex - cmb - 0.0244 # less Saverco's 24,400 shares
print(f'CMB NV: {cmb/sh_ex:.1%} of shares outside treasury (56.56% of issued); free float {float_:.1f}m shares')
print(f'US register: {us_register/sh_ex:.1%} of shares outside treasury; short interest {short/float_:.1%} of free float, {short/adv:.1f} days of US volume')
# green fleet: what charter rate a conventional-cost Newcastlemax needs for an 8% return over 25 years.
# cost proxy: Capesize newbuild $77m (Compass, 16 Nov 2026) scaled by 210k/180k dwt. opex $7,039/day (Q3 2026 slide 13).
# scrap value ignored. ammonia ships cost more; the company doesn't disclose by how much.
P = 77 * 210 / 180
ann = P * 0.08 / (1 - 1.08 ** -25)
print(f'Newcastlemax cost proxy ${P:.1f}m; capital charge ${ann:.2f}m a year = ${ann*1e6/365:,.0f}/day; plus opex = ${ann*1e6/365+7039:,.0f}/day needed for 8%')
for prem in (0.10, 0.20, 0.30):
    a = P * (1 + prem) * 0.08 / (1 - 1.08 ** -25)
    print(f'  with a {prem:.0%} ammonia premium on cost: ${a*1e6/365+7039:,.0f}/day')
